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

import numpy as np
import sounddevice as sd
from pynput import keyboard
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import tools from the new tools directory
from tools.definitions import get_virtual_tool_definitions
from tools.lua_scripts import (
    INSPECT_SERVICE_LUA,
    READ_SCRIPT_LUA,
    EDIT_SCRIPT_LUA,
    PATCH_SCRIPT_LUA,
    GET_LOGS_LUA,
    CLEAR_LOGS_LUA,
    SEARCH_SCRIPTS_LUA,
    GET_OBJECT_INFO_LUA,
    FIND_REFS_LUA,
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
    MARKETPLACE_INFO_LUA,
    CREATE_SPAWNER_LUA,
)

# Load environment variables from .env
load_dotenv()

LUA_UTILS = """
local function safe_print(...)
    local args = {...}
    local result = {}
    for i, v in ipairs(args) do
            table.insert(result, tostring(v))
    end
    print(table.concat(result, " "))
end

_G.Helper = {
    getGround = function(pos)
        local params = RaycastParams.new()
        params.FilterDescendantsInstances = {workspace:FindFirstChild("Baseplate")}
        params.FilterType = Enum.RaycastFilterType.Include
        local ray = workspace:Raycast(pos + Vector3.new(0, 50, 0), Vector3.new(0, -100, 0), params)
        if not ray then
            ray = workspace:Raycast(pos + Vector3.new(0, 50, 0), Vector3.new(0, -100, 0))
        end
        return ray and ray.Position or pos
    end,
    getSpatialSummary = function()
        local summary = "--- Spatial Summary ---\\n"
        local spawn = workspace:FindFirstChildWhichIsA("SpawnLocation", true)
        if spawn then
            summary = summary .. string.format("Spawn: Pos=%s, Look=%s\\n", tostring(spawn.Position), tostring(spawn.CFrame.LookVector))
        end
        local baseplate = workspace:FindFirstChild("Baseplate")
        if baseplate then
            summary = summary .. string.format("Baseplate: Size=%s, Pos=%s\\n", tostring(baseplate.Size), tostring(baseplate.Position))
        end
        -- Find major model centers
        for _, child in pairs(workspace:GetChildren()) do
            if child:IsA("Model") and child.PrimaryPart then
                summary = summary .. string.format("Model '%s': Pos=%s\\n", child.Name, tostring(child.PrimaryPart.Position))
            end
        end
        return summary
    end,
    scatter = function(template, count, range, parent)
        if not template then return end
        for i = 1, count do
            local clone = template:Clone()
            local x = (math.random() - 0.5) * range * 2
            local z = (math.random() - 0.5) * range * 2
            clone.Parent = parent or workspace
            local ground = _G.Helper.getGround(Vector3.new(x, 0, z))
            if clone:IsA("Model") then
                clone:MoveTo(ground)
            else
                clone.Position = ground + Vector3.new(0, clone.Size.Y/2, 0)
            end
        end
    end,
    setBaseplate = function(size, color, material)
        local b = workspace:FindFirstChild("Baseplate")
        if not b then
            b = Instance.new("Part")
            b.Name = "Baseplate"
            b.Parent = workspace
        end
        b.Size = typeof(size) == "Vector3" and size or Vector3.new(size, 10, size)
        b.Color = color or b.Color
        b.Material = material or b.Material
        b.Anchored = true
        b.Position = Vector3.new(0, -b.Size.Y/2, 0)
    end
}
"""


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

        self.client = genai.Client(api_key=self.api_key)
        self.model_id = model_id
        self.mcp_path = (
            "/Applications/RobloxStudioMCP.app/Contents/MacOS/rbx-studio-mcp"
        )

    async def _handle_tool_call(self, session, tc):
        """Executes a single tool call and returns the result text."""

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
                else:
                    val_str = f'"{str(v)}"'
                items.append(f"{key_str} = {val_str}")
            return "{" + ", ".join(items) + "}"

        mcp_res = None
        res_text = None

        if tc.name == "inspect_service":
            service = tc.args.get("service_name", "Workspace")
            depth = tc.args.get("depth", 4)
            print(f"[*] Inspecting {service} hierarchy (depth {depth})...")
            lua_command = INSPECT_SERVICE_LUA.format(
                service=service, depth=depth
            )
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "read_script_source":
            script_path = tc.args["script_path"]
            print(f"[*] Reading script source: {script_path}...")
            lua_command = READ_SCRIPT_LUA.format(script_path=script_path)
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "edit_script_source":
            script_path = tc.args["script_path"]
            new_source = tc.args["new_source"]
            print(f"[*] Editing script: {script_path}...")
            lua_command = EDIT_SCRIPT_LUA.format(
                script_path=script_path, new_source=new_source
            )
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "patch_script_source":
            script_path = tc.args["script_path"]
            search_string = tc.args["search_string"]
            replace_string = tc.args["replace_string"]
            print(f"[*] Patching script: {script_path}...")
            lua_command = PATCH_SCRIPT_LUA.format(
                script_path=script_path,
                search_string=search_string,
                replace_string=replace_string,
            )
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "get_studio_logs":
            count = tc.args.get("line_count", 50)
            print(f"[*] Fetching last {count} lines of Studio logs...")
            lua_command = GET_LOGS_LUA.format(count=count)
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "clear_studio_logs":
            print(f"[*] Marking start of new debug session in logs...")
            mcp_res = await session.call_tool(
                "run_code", {"command": CLEAR_LOGS_LUA}
            )
            res_text = "Debug session separator printed in Studio Output."

        elif tc.name == "search_scripts":
            pattern = tc.args["pattern"]
            print(f"[*] Searching scripts for: '{pattern}'...")
            lua_command = SEARCH_SCRIPTS_LUA.format(pattern=pattern)
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "get_object_info":
            path = tc.args["path"]
            print(f"[*] Fetching info for: {path}...")
            lua_command = GET_OBJECT_INFO_LUA.format(path=path)
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "find_script_references":
            target_name = tc.args["target_name"]
            print(f"[*] Finding references for: '{target_name}'...")
            lua_command = FIND_REFS_LUA.format(target_name=target_name)
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "manage_tags":
            action = tc.args["action"]
            tag = tc.args["tag"]
            path = tc.args.get("path", "nil")
            print(f"[*] Managing tag '{tag}' (Action: {action})...")
            lua_command = MANAGE_TAGS_LUA.format(
                path=path, action=action, tag=tag
            )
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "run_unit_tests":
            print(f"[*] Running unit tests...")
            mcp_res = await session.call_tool(
                "run_code", {"command": RUN_TESTS_LUA}
            )

        elif tc.name == "get_performance_stats":
            print(f"[*] Fetching performance stats...")
            mcp_res = await session.call_tool(
                "run_code", {"command": GET_STATS_LUA}
            )

        elif tc.name == "get_properties":
            path = tc.args["path"]
            print(f"[*] Fetching properties for: {path}...")
            lua_command = GET_PROPERTIES_LUA.format(path=path)
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "set_property":
            path = tc.args["path"]
            prop = tc.args["property"]
            val = tc.args["value"]
            print(f"[*] Setting {prop} on {path} to {val}...")
            lua_command = SET_PROPERTY_LUA.format(
                path=path, property=prop, value=val
            )
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "find_instances":
            root = tc.args.get("root_path", "game")
            cls = tc.args.get("class_name", "")
            pat = tc.args.get("name_pattern", "")
            print(
                f"[*] Finding instances in {root} (Class: {cls}, Pat: {pat})..."
            )
            lua_command = FIND_INSTANCES_LUA.format(
                root_path=root, class_name=cls, name_pattern=pat
            )
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "create_instance":
            cls = tc.args["class_name"]
            parent = tc.args["parent_path"]
            name = tc.args.get("name", cls)
            props = tc.args.get("properties", {})
            print(f"[*] Creating {cls} '{name}' in {parent}...")
            lua_command = CREATE_INSTANCE_LUA.format(
                class_name=cls,
                parent_path=parent,
                name=name,
                props_table=dict_to_lua_table(props),
            )
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "delete_instance":
            path = tc.args["path"]
            print(f"[*] Deleting instance: {path}...")
            lua_command = DELETE_INSTANCE_LUA.format(path=path)
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "raycast_check":
            origin = tc.args["origin"]
            direction = tc.args["direction"]
            print(f"[*] Casting ray from {origin}...")
            lua_command = RAYCAST_LUA.format(origin=origin, direction=direction)
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "publish_game":
            print(f"[*] Publishing game to Roblox Cloud...")
            mcp_res = await session.call_tool(
                "run_code", {"command": PUBLISH_GAME_LUA}
            )

        elif tc.name == "modify_instance":
            path = tc.args["path"]
            props = tc.args["properties"]
            print(f"[*] Bulk modifying properties on {path}...")
            lua_command = MODIFY_INSTANCE_LUA.format(
                path=path, props_table=dict_to_lua_table(props)
            )
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "get_studio_state":
            print(f"[*] Fetching Studio state...")
            mcp_res = await session.call_tool(
                "run_code", {"command": GET_STUDIO_STATE_LUA}
            )

        elif tc.name == "manipulate_terrain":
            action = tc.args["action"]
            pos = tc.args["position"]
            size = tc.args["size"]
            mat = tc.args.get("material", "Grass")
            print(f"[*] Manipulating terrain ({action}, {mat}) at {pos}...")
            lua_command = MANIPULATE_TERRAIN_LUA.format(
                action=action, position=pos, size=size, material=mat
            )
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "generate_procedural_terrain":
            pos_str = tc.args["position"]
            size_str = tc.args["size"]
            scale = tc.args.get("scale", 100)
            amp = tc.args.get("amplitude", 50)
            mat = tc.args.get("material", "Grass")
            biome = tc.args.get("biome", "hills")

            # Parse position and size
            px, py, pz = pos_str.replace(" ", "").split(",")
            width, depth = size_str.replace(" ", "").split(",")

            print(
                f"[*] Generating {biome} terrain ({width}x{depth}) at {pos_str}..."
            )
            lua_command = GENERATE_TERRAIN_LUA.format(
                x=px,
                y=py,
                z=pz,
                width=width,
                depth=depth,
                scale=scale,
                amplitude=amp,
                material=mat,
                biome=biome,
            )
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "smart_setup_asset":
            query = tc.args["query"]
            pos = tc.args.get("position", "0,5,0")
            print(f"[*] Smart-setting up asset: {query} at {pos}...")
            lua_command = SMART_SETUP_LUA.format(query=query, position=pos)
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "scatter_objects":
            path = tc.args["path"]
            count = tc.args.get("count", 10)
            radius = tc.args.get("radius", 100)
            print(f"[*] Scattering {count} instances of {path}...")
            lua_command = SCATTER_LUA.format(
                path=path, count=count, radius=radius
            )
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "inspect_marketplace_item":
            asset_id = tc.args["asset_id"]
            print(f"[*] Inspecting marketplace item: {asset_id}...")
            lua_command = MARKETPLACE_INFO_LUA.format(asset_id=asset_id)
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        elif tc.name == "create_timed_spawner":
            template_path = tc.args["template_path"]
            container_name = tc.args.get("container_name", "SpawnedObjects")
            interval = tc.args.get("interval", 5)
            max_count = tc.args.get("max_count", 10)
            spawn_area_center = tc.args.get("spawn_area_center", "0,10,0")
            spawn_radius = tc.args.get("spawn_radius", 100)

            print(f"[*] Creating timed spawner for {template_path}...")
            lua_command = CREATE_SPAWNER_LUA.format(
                template_path=template_path,
                container_name=container_name,
                interval=interval,
                max_count=max_count,
                spawn_area_center=spawn_area_center,
                spawn_radius=spawn_radius,
            )
            mcp_res = await session.call_tool(
                "run_code", {"command": lua_command}
            )

        else:
            print(f"[*] Executing {tc.name} in Roblox Studio...")
            cmd = tc.args.get("command") or tc.args.get("code")
            if tc.name == "run_code" and cmd:
                # Prepend utils to run_code
                cmd = LUA_UTILS + cmd
                mcp_res = await session.call_tool("run_code", {"command": cmd})
            else:
                # Ensure we use 'command' if it's an MCP tool that might expect it
                args = tc.args.copy()
                if "code" in args:
                    args["command"] = args.pop("code")
                mcp_res = await session.call_tool(tc.name, args)

        # Unified response processing and error detection
        if mcp_res and res_text is None:
            res_text = "\n".join(
                [c.text for c in mcp_res.content if hasattr(c, "text")]
            )

        if res_text is not None:
            # Detect Studio/Lua errors in the response text
            is_lua_error = (
                "Error:" in res_text
                or "Unable to assign" in res_text
                or "failed" in res_text.lower()
                or "not found" in res_text.lower()
                or "attempt to index" in res_text.lower()
                or "nil value" in res_text.lower()
                or "unexpected" in res_text.lower()
                or "traceback" in res_text.lower()
            )

            if (mcp_res and getattr(mcp_res, "isError", False)) or is_lua_error:
                print(f"[!] Tool execution failed. Fetching logs...")
                if not res_text.startswith("Error:"):
                    res_text = f"Error: {res_text}"

                # Automatically append recent logs on error
                try:
                    lua_logs = GET_LOGS_LUA.format(count=10)
                    log_res = await session.call_tool(
                        "run_code", {"command": lua_logs}
                    )
                    if log_res and log_res.content:
                        log_text = "\n".join(
                            [
                                c.text
                                for c in log_res.content
                                if hasattr(c, "text")
                            ]
                        )
                        res_text += f"\n\n--- AUTO-FETCHED LOGS ---\n{log_text}"
                except Exception as e:
                    res_text += f"\n(Failed to auto-fetch logs: {e})"
            else:
                print(f"[√] Success.")

        return res_text or "No response from Studio."

    async def _setup_mcp_session(self):
        """Starts the MCP process and returns the session protocol components."""
        from mcp.client.stdio import StdioServerParameters, stdio_client
        from mcp import ClientSession
        import mcp.types as mcp_types

        process = await asyncio.create_subprocess_exec(
            self.mcp_path,
            "--stdio",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=os.environ.copy(),
        )

        async def log_stderr():
            try:
                while True:
                    line = await process.stderr.readline()
                    if not line:
                        break
                    print(
                        f"[Roblox Server Log] {line.decode().strip()}",
                        file=sys.stderr,
                    )
            except Exception:
                pass

        stderr_task = asyncio.create_task(log_stderr())

        params = StdioServerParameters(
            command=self.mcp_path, args=["--stdio"], env=os.environ.copy()
        )

        return process, stderr_task, stdio_client(params)

    def _get_gemini_config(self, mcp_tools):
        """Creates the Gemini model configuration with both MCP and virtual tools."""

        def clean_schema(schema):
            if isinstance(schema, dict):
                return {
                    k: clean_schema(v)
                    for k, v in schema.items()
                    if k != "$schema"
                }
            return schema

        # Convert MCP tools to Gemini format
        gemini_tools = [
            types.FunctionDeclaration(
                name=t.name,
                description=t.description,
                parameters=clean_schema(t.inputSchema),
            )
            for t in mcp_tools
        ]

        # Add virtual tools
        gemini_tools.extend(get_virtual_tool_definitions())

        return types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=gemini_tools)],
            system_instruction=(
                "You are an Elite Roblox Studio Game Engineer and AI Agent. You don't just write code; you build and debug live game worlds.\n\n"
                "YOUR CORE PRINCIPLES:\n"
                "1. TRUST YOUR TOOLS: Your building tools (`smart_setup_asset`, `generate_procedural_terrain`, `create_instance`) now have built-in Ground-Awareness. They automatically snap objects to the terrain surface. You no longer need to calculate complex Y-coordinates. Focus on X and Z; the system handles the floor.\n"
                "2. EFFICIENCY: Use 'modify_instance' to style objects in a single turn. Use 'smart_setup_asset' to search and setup weapons/NPCs in ONE turn. Use 'create_timed_spawner' to automate object spawning instead of writing manual scripts.\n"
                "3. CONTEXT AWARENESS: Use 'get_studio_state' to see if you are in Edit Mode or Play Mode. Remember: objects spawned by scripts only exist in Play Mode.\n"
                "4. MARKETPLACE STRATEGY: Use 'smart_setup_asset' for complex items. If unsure about an asset, use 'inspect_marketplace_item' first to see its description and class contents.\n"
                "5. TERRAIN & ENVIRONMENT: Use 'generate_procedural_terrain' for large landscapes. The system will automatically move the player's spawn to the new surface. Use 'scatter_objects' to distribute environmental props automatically.\n"
                "6. GENERALIZATION: Build systems that work for any game type. Favor atomic tools over monolithic Lua scripts. Use generic containers and naming conventions.\n"
                "7. DEBUGGING: Be proactive. After editing any script, you MUST verify the logs using 'get_studio_logs'. Do not wait for the user. If an asset fails to load (check logs!) or a property seems wrong, use 'get_studio_state' or 'get_studio_logs' to see the exact error.\n"
                "8. LIMITATIONS: Note that 'Technology' (ShadowMap/Future) cannot be set via script due to engine security. Don't try to change it; just work with what's there.\n"
                "9. SPATIAL LOGIC: Floor bounds are half-size. A 50-stud floor at (0,0,0) ends at +/- 25 on X and Z. Spawning NPCs at Z=30 will cause them to fall into the void. Default LookVector is (0,0,-1); to face a counter at +Z, rotate the SpawnLocation 180 degrees.\n"
                "10. DATA TYPES: Properties like TorsoColor require 'BrickColor'. Use 'BrickColor.new(color3_value)' if you only have RGB. Your Lua tools will try to auto-convert, but be explicit when possible.\n\n"
                "WORKFLOW:\n"
                "- If a unit isn't moving: Check 'Anchored' and 'HipHeight' using 'get_properties'. Verify if simulation is running with 'get_studio_state'.\n"
                "- If building: Run 'generate_procedural_terrain' first. The system will automatically move the player's spawn to the new surface. Use 'smart_setup_asset' for characters and weapons; they will land on the ground automatically.\n"
                "- Deployment: Use 'publish_game' when the user is happy. INFORM them it requires manual confirmation (y/n).\n\n"
                "CRITICAL: Be proactive. If you find a bug, FIX IT immediately using your manipulation tools. Don't just suggest the fix; apply it."
            ),
            thinking_config=types.ThinkingConfig(include_thoughts=True),
        )

    async def _process_request(self, session, config, history, content_parts):
        """Internal method to run a Gemini generation cycle, can be cancelled."""
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

                if tool_calls:
                    response_parts = []
                    for tc in tool_calls:
                        res_text = await self._handle_tool_call(session, tc)
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
            # We don't append to history on cancellation to keep it clean
            raise
        except Exception as e:
            print(f"\n[!] Error in process_request: {e}")
            traceback.print_exc()

    async def run_interactive(self):
        print(f"[*] Starting Roblox MCP binary...")
        process, stderr_task, stdio_mgr = await self._setup_mcp_session()

        try:
            from mcp import ClientSession
            import mcp.types as mcp_types

            print("[*] Connecting to MCP...")
            async with stdio_mgr as (read, write):
                async with ClientSession(read, write) as session:
                    print("[*] Initializing Protocol...")
                    await session.initialize()
                    await session.send_notification(
                        mcp_types.InitializedNotification()
                    )

                    print("[*] Fetching Tools...")
                    tools_resp = await session.list_tools()
                    config = self._get_gemini_config(tools_resp.tools)

                    print(
                        f"[*] Connected! Tools found: {', '.join(t.name for t in tools_resp.tools)}, and 13 virtual tools."
                    )

                    history = []
                    event_queue = asyncio.Queue()
                    voice_manager = VoiceManager(event_queue)

                    print(f"\n=== Roblox AI Studio ({self.model_id}) ===")
                    print(
                        "Usage: Type commands or HOLD [Right Command] to speak."
                    )
                    print("Type 'exit' to quit.")

                    loop = asyncio.get_running_loop()

                    def input_thread():
                        while True:
                            try:
                                text = input("\n> ")
                                if text.lower() in ["exit", "quit", "q"]:
                                    loop.call_soon_threadsafe(
                                        event_queue.put_nowait,
                                        TextInputEvent("exit"),
                                    )
                                    break
                                loop.call_soon_threadsafe(
                                    event_queue.put_nowait, TextInputEvent(text)
                                )
                            except EOFError:
                                break

                    threading.Thread(target=input_thread, daemon=True).start()

                    async with asyncio.TaskGroup() as tg:
                        current_task = None

                        # Start the microphone stream
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
                                            session,
                                            config,
                                            history,
                                            [
                                                types.Part.from_text(
                                                    text=event.text
                                                )
                                            ],
                                        )
                                    )

                                elif isinstance(event, PTTStartEvent):
                                    if current_task and not current_task.done():
                                        print(
                                            "\n[*] Interrupting for voice input..."
                                        )
                                        current_task.cancel()

                                elif isinstance(event, PTTEndEvent):
                                    if not event.audio_data:
                                        print("[!] No audio captured.")
                                        continue

                                    current_task = tg.create_task(
                                        self._process_request(
                                            session,
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

        except Exception as e:
            if not isinstance(e, (asyncio.CancelledError, KeyboardInterrupt)):
                print(f"\n[!] Fatal Error: {e}")
                traceback.print_exc()
        finally:
            stderr_task.cancel()
            if "process" in locals() and process.returncode is None:
                try:
                    process.terminate()
                    await process.wait()
                except:
                    pass


if __name__ == "__main__":
    wrapper = RobloxAIWrapper()
    asyncio.run(wrapper.run_interactive())
