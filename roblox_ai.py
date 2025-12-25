import asyncio
import os
import sys
import json
import traceback
import io
import wave
import threading
from dataclasses import dataclass
from typing import Optional, List, Any
import httpx  # For talking to the local server

import numpy as np
import sounddevice as sd  #
from pynput import keyboard
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import tools from the new tools directory
from tools.definitions import get_virtual_tool_definitions
from tools.planner import PlanManager
from tools.lua_scripts import (
    INSPECT_SERVICE_LUA,
    READ_SCRIPT_LUA,
    EDIT_SCRIPT_LUA,
    PATCH_SCRIPT_LUA,
    GET_LOGS_LUA,
    CLEAR_LOGS_LUA,
    SEARCH_SCRIPTS_LUA,
    GET_OBJECT_INFO_LUA,
    MANAGE_TAGS_LUA,
    RUN_TESTS_LUA,
    GET_STATS_LUA,
    GET_PROPERTIES_LUA,
    SET_PROPERTY_LUA,
    FIND_INSTANCES_LUA,
    CREATE_INSTANCE_LUA,
    DELETE_INSTANCE_LUA,
    RAYCAST_LUA,
    PUBLISH_GAME_LUA,
    MODIFY_INSTANCE_LUA,
    GET_STUDIO_STATE_LUA,
    MANIPULATE_TERRAIN_LUA,
    GENERATE_TERRAIN_LUA,
    SMART_SETUP_LUA,
    SCATTER_LUA,
    CREATE_SPAWNER_LUA,
    GET_SPATIAL_SUMMARY_LUA,
    SEARCH_MARKETPLACE_LUA,
    REPARENT_INSTANCE_LUA,
    CONNECT_PARTS_LUA,
)

# Load environment variables from .env
load_dotenv()


@dataclass
class PTTStartEvent:
    pass


@dataclass
class PTTEndEvent:
    audio_data: bytes


@dataclass
class TextInputEvent:
    text: str


class VoiceManager:
    def __init__(self, event_queue: asyncio.Queue):
        self.event_queue = event_queue
        self.fs = 16000
        self.audio_buffer: List[np.ndarray] = []
        self.is_recording = False
        self.loop = asyncio.get_event_loop()
        self.ptt_key = keyboard.Key.cmd_r  # Right Command Key

        # Initialize the keyboard listener in a separate thread
        self.listener = keyboard.Listener(
            on_press=self._on_press, on_release=self._on_release
        )
        self.listener.start()

    def _audio_callback(self, indata, frames, time, status):
        if self.is_recording:
            self.audio_buffer.append(indata.copy())

    def _on_press(self, key):
        if key == self.ptt_key and not self.is_recording:
            self.is_recording = True
            self.audio_buffer = []
            print("\n[LISTENING...]", end="", flush=True)
            self.loop.call_soon_threadsafe(
                self.event_queue.put_nowait, PTTStartEvent()
            )

    def _on_release(self, key):
        if key == self.ptt_key and self.is_recording:
            self.is_recording = False
            print(" [DONE]")
            audio_bytes = self._finalize_audio()
            self.loop.call_soon_threadsafe(
                self.event_queue.put_nowait, PTTEndEvent(audio_bytes)
            )

    def _finalize_audio(self) -> bytes:
        if not self.audio_buffer:
            return b""
        audio_data = np.concatenate(self.audio_buffer, axis=0)
        # Convert to int16 for WAV
        audio_int16 = (audio_data * 32767).astype(np.int16)

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.fs)
            wf.writeframes(audio_int16.tobytes())
        return buffer.getvalue()

    def start_mic_stream(self):
        return sd.InputStream(
            samplerate=self.fs, channels=1, callback=self._audio_callback
        )


class RobloxAIWrapper:
    def __init__(
        self,
        api_key: str | None = None,
        model_id: str = "gemini-3-flash-preview",
    ):
        self.api_key = (
            api_key
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
        )
        if not self.api_key:
            print(
                "Error: API Key not found. Please set GEMINI_API_KEY in your .env file."
            )
            sys.exit(1)

        # Gemini Client Configuration with retry logic
        retry_options = types.HttpRetryOptions(
            attempts=5,
            initial_delay=2.0,
            max_delay=60.0,
            exp_base=2.0,
            jitter=0.1,
            http_status_codes=[429, 503, 404],
        )
        http_options = types.HttpOptions(
            api_version="v1beta", retry_options=retry_options
        )

        self.client = genai.Client(
            api_key=self.api_key, http_options=http_options
        )
        self.model_id = model_id

        # New API Connection
        self.api_url = "http://127.0.0.1:8000"
        self.http_client = httpx.AsyncClient(timeout=30.0)

        self.plan_manager = PlanManager()
        self.n_last_thoughts = int(os.environ.get("N_LAST_THOUGHTS", 3))

    async def _handle_tool_call(self, tc):
        """Executes a single tool call by sending it to the local API server."""

        def dict_to_lua_table(d):
            if not d:
                return "{}"
            items = []
            for k, v in d.items():
                key_str = f'["{k}"]'
                if isinstance(v, bool):
                    val_str = "true" if v else "false"
                elif isinstance(v, (int, float)):
                    val_str = str(v)
                elif isinstance(v, str):
                    val_str = f"[===[{v}]===]"
                elif isinstance(v, dict):
                    val_str = dict_to_lua_table(v)
                elif isinstance(v, list):
                    val_str = (
                        "{"
                        + ", ".join([dict_to_lua_table(item) for item in v])
                        + "}"
                    )
                else:
                    val_str = f'"{str(v)}"'
                items.append(f"{key_str} = {val_str}")
            return "{" + ", ".join(items) + "}"

        def fix_path(path):
            if not path or not isinstance(path, str):
                return path
            services = [
                "Workspace",
                "Lighting",
                "ReplicatedStorage",
                "ServerStorage",
                "ServerScriptService",
                "StarterGui",
                "StarterPack",
                "Players",
                "LogService",
                "RunService",
                "SoundService",
                "CollectionService",
                "TweenService",
                "Debris",
            ]
            path_lower = path.lower()
            for s in services:
                s_lower = s.lower()
                if path_lower == s_lower or path_lower.startswith(
                    s_lower + "."
                ):
                    suffix = path[len(s) :] if len(path) > len(s) else ""
                    return f"game.{s}{suffix}"
            if (
                path == "game"
                or path.startswith("game.")
                or path.startswith("workspace")
            ):
                return path
            return path

        async def run_studio_code(lua_command):
            # Send code to the server's queue
            try:
                resp = await self.http_client.post(
                    f"{self.api_url}/queue",
                    json={"user_id": "default_user", "code": lua_command},
                )
                if resp.status_code != 200:
                    return f"Error queuing code: {resp.text}"

                cmd_data = resp.json()
                cmd_id = cmd_data.get("id")

                print(
                    f" [Queued: {cmd_id}] Waiting for Studio execution...",
                    end="",
                    flush=True,
                )

                # Poll for result (timeout after 30s)
                for _ in range(60):
                    await asyncio.sleep(0.5)
                    res_resp = await self.http_client.get(
                        f"{self.api_url}/result/{cmd_id}"
                    )
                    if res_resp.status_code == 200:
                        data = res_resp.json()
                        if data["status"] == "completed":
                            print(" [Done]")
                            result_data = data["result"]
                            # The plugin returns { success: bool, output: str, error: str }
                            # We want to return just the string text for the AI
                            if isinstance(result_data, dict):
                                if result_data.get("success"):
                                    return result_data.get("output", "Success")
                                else:
                                    return f"Error: {result_data.get('error') or result_data.get('output')}"
                            return str(result_data)

                print(" [Timeout]")
                return "Error: Timeout waiting for Roblox Studio to execute command. Is the plugin connected?"

            except Exception as e:
                return f"Failed to connect to Vibe Coder Server: {e}"

        mcp_res = None

        # --- TOOL MAPPING ---
        lua_command = None

        if tc.name == "inspect_service":
            service = tc.args.get("service_name", "Workspace")
            depth = tc.args.get("depth", 4)
            print(f"[*] Inspecting {service} hierarchy (depth {depth})...")
            lua_command = INSPECT_SERVICE_LUA.format(
                service=service, depth=depth
            )

        elif tc.name == "read_script_source":
            script_path = fix_path(tc.args["script_path"])
            print(f"[*] Reading script source: {script_path}...")
            lua_command = READ_SCRIPT_LUA.format(script_path=script_path)

        elif tc.name == "edit_script_source":
            script_path = fix_path(tc.args["script_path"])
            new_source = tc.args["new_source"]
            print(f"[*] Editing script: {script_path}...")
            lua_command = EDIT_SCRIPT_LUA.format(
                script_path=script_path, new_source=new_source
            )

        elif tc.name == "patch_script_source":
            script_path = fix_path(tc.args["script_path"])
            search_string = tc.args["search_string"]
            replace_string = tc.args.get("replace_string") or tc.args.get(
                "patch_string"
            )
            if not replace_string:
                return "Error: Missing 'replace_string'."
            print(f"[*] Patching script: {script_path}...")
            lua_command = PATCH_SCRIPT_LUA.format(
                script_path=script_path,
                search_string=search_string,
                replace_string=replace_string,
            )

        elif tc.name == "get_studio_logs":
            count = tc.args.get("line_count", 50)
            print(f"[*] Fetching last {count} lines of Studio logs...")
            lua_command = GET_LOGS_LUA.format(count=count)

        elif tc.name == "clear_studio_logs":
            print(f"[*] Marking start of new debug session in logs...")
            lua_command = CLEAR_LOGS_LUA

        elif tc.name == "search_scripts":
            pattern = tc.args["pattern"]
            print(f"[*] Searching scripts for: '{pattern}'...")
            lua_command = SEARCH_SCRIPTS_LUA.format(pattern=pattern)

        elif tc.name == "get_object_info":
            path = fix_path(tc.args["path"])
            print(f"[*] Fetching info for: {path}...")
            lua_command = GET_OBJECT_INFO_LUA.format(path=path)

        elif tc.name == "manage_tags":
            action = tc.args["action"]
            tag = tc.args["tag"]
            path = fix_path(tc.args.get("path", "nil"))
            print(f"[*] Managing tag '{tag}' (Action: {action})...")
            lua_command = MANAGE_TAGS_LUA.format(
                path=path, action=action, tag=tag
            )

        elif tc.name == "run_unit_tests":
            print(f"[*] Running unit tests...")
            lua_command = RUN_TESTS_LUA

        elif tc.name == "get_performance_stats":
            print(f"[*] Fetching performance stats...")
            lua_command = GET_STATS_LUA

        elif tc.name == "get_properties":
            path = fix_path(tc.args["path"])
            print(f"[*] Fetching properties for: {path}...")
            lua_command = GET_PROPERTIES_LUA.format(path=path)

        elif tc.name == "set_property":
            path = fix_path(tc.args["path"])
            prop = tc.args["property"]
            val = tc.args["value"]
            print(f"[*] Setting {prop} on {path} to {val}...")
            lua_command = SET_PROPERTY_LUA.format(
                path=path, property=prop, value=val
            )

        elif tc.name == "find_instances":
            root = fix_path(tc.args.get("root_path", "game"))
            cls = tc.args.get("class_name", "")
            pat = tc.args.get("name_pattern", "")
            print(
                f"[*] Finding instances in {root} (Class: {cls}, Pat: {pat})..."
            )
            lua_command = FIND_INSTANCES_LUA.format(
                root_path=root, class_name=cls, name_pattern=pat
            )

        elif tc.name == "create_instance":
            cls = tc.args["class_name"]
            parent = fix_path(tc.args["parent_path"])
            name = tc.args.get("name", cls)
            props = tc.args.get("properties", {})
            children = tc.args.get("children", [])

            def children_to_lua(kids):
                if not kids:
                    return "{}"
                items = []
                for kid in kids:
                    k_cls = kid.get("class_name")
                    k_name = kid.get("name", k_cls)
                    k_props = dict_to_lua_table(kid.get("properties", {}))
                    k_kids = children_to_lua(kid.get("children", []))
                    items.append(
                        f'{{class_name="{k_cls}", name="{k_name}", properties={k_props}, children={k_kids}}}'
                    )
                return "{" + ", ".join(items) + "}"

            print(f"[*] Creating {cls} '{name}' in {parent}...")
            lua_command = CREATE_INSTANCE_LUA.format(
                class_name=cls,
                parent_path=parent,
                name=name,
                props_table=dict_to_lua_table(props),
                children_table=children_to_lua(children),
            )

        elif tc.name == "delete_instance":
            path = fix_path(tc.args["path"])
            print(f"[*] Deleting instance: {path}...")
            lua_command = DELETE_INSTANCE_LUA.format(path=path)

        elif tc.name == "raycast_check":
            origin = tc.args["origin"]
            direction = tc.args["direction"]
            print(f"[*] Casting ray from {origin}...")
            lua_command = RAYCAST_LUA.format(origin=origin, direction=direction)

        elif tc.name == "publish_game":
            print(f"[*] Publishing game to Roblox Cloud...")
            lua_command = PUBLISH_GAME_LUA

        elif tc.name == "modify_instance":
            path = fix_path(tc.args["path"])
            props = tc.args["properties"]
            print(f"[*] Bulk modifying properties on {path}...")
            lua_command = MODIFY_INSTANCE_LUA.format(
                path=path, props_table=dict_to_lua_table(props)
            )

        elif tc.name == "get_studio_state":
            print(f"[*] Fetching Studio state...")
            lua_command = GET_STUDIO_STATE_LUA

        elif tc.name == "manipulate_terrain":
            action = tc.args["action"]
            pos = tc.args["position"]
            size = tc.args["size"]
            mat = tc.args.get("material", "Grass")
            print(f"[*] Manipulating terrain ({action}, {mat}) at {pos}...")
            lua_command = MANIPULATE_TERRAIN_LUA.format(
                action=action, position=pos, size=size, material=mat
            )

        elif tc.name == "generate_procedural_terrain":
            pos_str = tc.args["position"]
            size_str = tc.args["size"]
            # ... (parsing logic same as before)
            px, py, pz = pos_str.replace(" ", "").split(",")
            width, depth = size_str.replace(" ", "").split(",")
            print(f"[*] Generating terrain...")
            lua_command = GENERATE_TERRAIN_LUA.format(
                x=px,
                y=py,
                z=pz,
                width=width,
                depth=depth,
                scale=tc.args.get("scale", 100),
                amplitude=tc.args.get("amplitude", 50),
                material=tc.args.get("material", "Grass"),
                biome=tc.args.get("biome", "hills"),
            )

        elif tc.name == "smart_setup_asset":
            query = tc.args["query"]
            pos = tc.args.get("position", "0,5,0")
            print(f"[*] Smart-setting up asset: {query}...")
            lua_command = SMART_SETUP_LUA.format(query=query, position=pos)

        elif tc.name == "search_marketplace":
            query = tc.args["query"]
            asset_type = tc.args.get("asset_type", "Model")
            print(f"[*] Searching marketplace: {query}...")
            lua_command = SEARCH_MARKETPLACE_LUA.format(
                query=query, asset_type=asset_type
            )

        elif tc.name == "reparent_instance":
            path = fix_path(tc.args["path"])
            new_parent = fix_path(tc.args["new_parent"])
            print(f"[*] Reparenting {path}...")
            lua_command = REPARENT_INSTANCE_LUA.format(
                path=path, new_parent=new_parent
            )

        elif tc.name == "scatter_objects":
            path = fix_path(tc.args["path"])
            # ... (args same as before)
            print(f"[*] Scattering objects...")
            lua_command = SCATTER_LUA.format(
                path=path,
                count=tc.args.get("count", 10),
                radius=tc.args.get("radius", 100),
                align_to_surface=str(
                    tc.args.get("align_to_surface", True)
                ).lower(),
                random_rotation=str(
                    tc.args.get("random_rotation", True)
                ).lower(),
            )

        elif tc.name == "create_timed_spawner":
            print(f"[*] Creating timed spawner...")
            lua_command = CREATE_SPAWNER_LUA.format(
                template_path=fix_path(tc.args["template_path"]),
                container_name=tc.args.get("container_name", "SpawnedObjects"),
                interval=tc.args.get("interval", 5),
                max_count=tc.args.get("max_count", 10),
                spawn_area_center=tc.args.get("spawn_area_center", "0,10,0"),
                spawn_radius=tc.args.get("spawn_radius", 100),
            )

        elif tc.name == "get_spatial_summary":
            print(f"[*] Fetching relative spatial summary...")
            lua_command = GET_SPATIAL_SUMMARY_LUA

        elif tc.name == "connect_parts":
            print(f"[*] Connecting parts...")
            lua_command = CONNECT_PARTS_LUA.format(
                part_a=fix_path(tc.args["part_a"]),
                part_b=fix_path(tc.args["part_b"]),
                constraint_type=tc.args.get("constraint_type", "Weld"),
                axis=tc.args.get("axis", "Y"),
                anchor_mode=tc.args.get("anchor_mode", "Center"),
            )

        elif tc.name == "run_code":
            cmd = tc.args.get("command") or tc.args.get("code")
            if cmd:
                lua_command = cmd

        # Execute
        if lua_command:
            return await run_studio_code(lua_command)

        return "Tool not implemented or no Lua command generated."

    def _get_gemini_config(self, mcp_tools=None):
        """Creates the Gemini model configuration with virtual tools."""

        # We only use virtual tools now, no MCP discovery needed
        gemini_tools = get_virtual_tool_definitions()

        return types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=gemini_tools)],
            system_instruction=(
                "You are an Elite Roblox Studio Game Engineer and AI Agent. You don't just write code; you build and debug live game worlds.\n\n"
                "YOUR CORE PRINCIPLES:\n"
                "1. SMART CREATION: Use `create_instance` with the `children` parameter to build entire UI hierarchies (ScreenGui -> Frame -> TextLabel) in a SINGLE step. Do not create objects one by one.\n"
                "2. TRUST YOUR TOOLS: Your building tools (`smart_setup_asset`, `create_instance`) have built-in Ground-Awareness. They automatically snap objects to the terrain surface. You do NOT need to calculate Y-coordinates for placement. Focus on X and Z.\n"
                "3. FORGIVING SYNTAX: You can use simple property values. Send 'Red' instead of 'Color3.fromRGB(255,0,0)'. Send '{0.5,0,0.5,0}' for UDim2. The system handles the conversion for you.\n"
                "4. ASSET WORKFLOW: \n"
                "   - To use an asset: 1) `search_marketplace('Sword')`. 2) Pick an ID. 3) `smart_setup_asset(id=...)`.\n"
                "   - `smart_setup_asset` AUTOMATICALLY puts Tools in StarterPack and NPCs in ServerStorage. You rarely need to move them manually.\n"
                "   - Only use `reparent_instance` if you have a specific non-standard goal (e.g., 'Give this specific Zombie a Sword').\n"
                "5. CONTEXT AWARENESS: Use 'get_studio_state' to see if you are in Edit Mode or Play Mode. Use 'get_spatial_summary' frequently to 'see' the world.\n"
                "6. DEBUGGING: Be proactive. If an asset fails to load or a property seems wrong, check the logs. Use `edit_script_source` to fix bugs immediately.\n"
                "7. SPATIAL LOGIC: Use `get_spatial_summary` to understand surroundings. +X is Right, -X is Left, +Y is Up, -Y is Down, -Z is Front, +Z is Back.\n"
                "8. SCRIPT EDITING: The system now pre-validates syntax. If you make a typo, the tool will reject the edit and tell you why. Fix it and try again.\n"
                "9. PHYSICS: Use `connect_parts` for all mechanical joints (welds, hinges). Do not try to manually create Attachments and Constraints with `create_instance`.\n\n"
                "WORKFLOW:\n"
                "- UI Design: Create the full structure in one `create_instance` call.\n"
                "- Building: Use `generate_procedural_terrain` then `smart_setup_asset`. Objects will land on the ground automatically.\n"
                "- Deployment: Use 'publish_game' when the user is happy (requires confirmation).\n\n"
                "CRITICAL: You are an expert. Don't ask for permission to use standard patterns. Just build it."
            ),
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
            ),
        )

    async def _process_request(self, config, history, content_parts):
        """Internal method to run a Gemini generation cycle."""
        try:
            history.append(types.Content(role="user", parts=content_parts))

            while True:
                print("\n[Thinking...]")
                current_response_parts = []
                tool_calls = []

                async for (
                    chunk
                ) in await self.client.aio.models.generate_content_stream(
                    model=self.model_id,
                    contents=history,
                    config=config,
                ):
                    if not chunk.candidates:
                        continue

                    for part in chunk.candidates[0].content.parts:
                        current_response_parts.append(part)
                        if part.thought:
                            print(part.text, end="", flush=True)
                        elif part.text:
                            print(part.text, end="", flush=True)
                        elif part.function_call:
                            tool_calls.append(part.function_call)
                            print(
                                f"\n\n[*] AI Call: {part.function_call.name}({json.dumps(part.function_call.args)})"
                            )

                history.append(
                    types.Content(
                        role="model",
                        parts=current_response_parts,
                    )
                )

                if self.n_last_thoughts != -1:
                    model_turn_count = 0
                    for i in range(len(history) - 1, -1, -1):
                        msg = history[i]
                        if msg.role == "model":
                            model_turn_count += 1
                            if model_turn_count > self.n_last_thoughts:
                                msg.parts = [
                                    p
                                    for p in msg.parts
                                    if not getattr(p, "thought", False)
                                ]

                if tool_calls:
                    response_parts = []
                    for tc in tool_calls:
                        res_text = await self._handle_tool_call(tc)
                        response_parts.append(
                            types.Part.from_function_response(
                                name=tc.name,
                                response={"result": res_text},
                            )
                        )

                    history.append(
                        types.Content(role="tool", parts=response_parts)
                    )
                    continue
                else:
                    break

            print("\n[√] Task Complete.")

        except asyncio.CancelledError:
            print("\n[!] Task Interrupted.")
            raise
        except Exception as e:
            print(f"\n[!] Error in process_request: {e}")
            traceback.print_exc()

    async def run_interactive(self):
        print(f"[*] Connecting to Plugin Server at {self.api_url}...")

        # We no longer need MCP connection logic
        config = self._get_gemini_config()

        history = []
        event_queue = asyncio.Queue()
        voice_manager = VoiceManager(event_queue)

        print(f"\n=== Roblox AI Studio ({self.model_id}) ===")
        print("Usage: Type commands or HOLD [Right Command] to speak.")
        print("Type 'exit' to quit.")

        loop = asyncio.get_running_loop()

        def input_thread():
            while True:
                try:
                    text = input("\n> ")
                    if not text:
                        continue
                    if text.lower() in ["exit", "quit", "q"]:
                        loop.call_soon_threadsafe(
                            event_queue.put_nowait,
                            TextInputEvent("exit"),
                        )
                        break

                    loop.call_soon_threadsafe(
                        event_queue.put_nowait, TextInputEvent(text)
                    )
                except (EOFError, KeyboardInterrupt):
                    loop.call_soon_threadsafe(
                        event_queue.put_nowait,
                        TextInputEvent("exit"),
                    )
                    break

        threading.Thread(target=input_thread, daemon=True).start()

        async with asyncio.TaskGroup() as tg:
            current_task = None

            with voice_manager.start_mic_stream():
                while True:
                    event = await event_queue.get()

                    if isinstance(event, TextInputEvent):
                        if event.text == "exit":
                            if current_task:
                                current_task.cancel()
                            break

                        if current_task and not current_task.done():
                            current_task.cancel()

                        current_task = tg.create_task(
                            self._process_request(
                                config,
                                history,
                                [types.Part.from_text(text=event.text)],
                            )
                        )

                    elif isinstance(event, PTTStartEvent):
                        if current_task and not current_task.done():
                            print("\n[*] Interrupting for voice input...")
                            current_task.cancel()

                    elif isinstance(event, PTTEndEvent):
                        if not event.audio_data:
                            print("[!] No audio captured.")
                            continue

                        current_task = tg.create_task(
                            self._process_request(
                                config,
                                history,
                                [
                                    types.Part.from_bytes(
                                        data=event.audio_data,
                                        mime_type="audio/wav",
                                    ),
                                    types.Part.from_text(
                                        text="Follow the instructions in this audio."
                                    ),
                                ],
                            )
                        )


if __name__ == "__main__":
    wrapper = RobloxAIWrapper()
    asyncio.run(wrapper.run_interactive())
