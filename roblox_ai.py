import asyncio
import os
import sys
import json
import traceback
import io
import wave
import threading
import argparse
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
        debug_mode: bool = False,
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
        self.debug_mode = debug_mode

        # New API Connection
        self.api_url = "http://127.0.0.1:8000"
        self.http_client = httpx.AsyncClient(timeout=30.0)

        self.plan_manager = PlanManager()
        self.n_last_thoughts = int(os.environ.get("N_LAST_THOUGHTS", 3))

    async def _handle_tool_call(self, tc):
        """Executes a tool call by loading Lua dynamically and passing args via JSON."""

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

                            if self.debug_mode:
                                print(
                                    f"\n[DEBUG] Raw Server Response: {json.dumps(result_data, indent=2)}"
                                )

                            # If debug_mode is on, return raw JSON to AI
                            if self.debug_mode:
                                return json.dumps(result_data)

                            # Normal mode: return string output
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

        # 1. Load the Tool Logic
        tool_file = os.path.join("tools", "lua", f"{tc.name}.lua")
        if not os.path.exists(tool_file):
            return f"Error: Tool implementation not found at {tool_file}"

        with open(tool_file, "r") as f:
            tool_code = f.read()

        # 2. Prepare the Safe Header and JSON Data
        args_json = json.dumps(tc.args)

        # SafeResolve handles hyphens, spaces, and bracket notation automatically
        safe_resolve_lua = """
local function SafeResolve(path)
    if not path or path == "" then return nil end
    if typeof(path) ~= "string" then return path end
    
    local current = game
    
    -- 1. Clean the path of bracket notation game.Workspace["Part Name"] -> game.Workspace.Part Name
    local cleanPath = path:gsub('%%["', "."):gsub('"%%]', ""):gsub("%%['", "."):gsub("'%%]", "")
    
    -- 2. Normalize separators
    cleanPath = cleanPath:gsub("/", "."):gsub("\\\\\\\\", ".")
    
    local parts = {}
    for part in cleanPath:gmatch("([^%%.]+)") do
        if part ~= "" then
            table.insert(parts, part)
        end
    end

    for i, name in ipairs(parts) do
        -- Skip 'game' if it's the first part
        if i == 1 and (name:lower() == "game" or name:lower() == "workspace") then
            if name:lower() == "workspace" then current = workspace end
        else
            local nextObj = current:FindFirstChild(name)
            
            -- If not found directly, and we're at game level, try GetService
            if not nextObj and current == game then
                local success, service = pcall(function() return game:GetService(name) end)
                if success and service then
                    nextObj = service
                end
            end
            
            if not nextObj then
                return nil, "Could not find child '" .. name .. "' in " .. current:GetFullName()
            end
            current = nextObj
        end
    end
    
    return current
end
"""

        full_lua_command = f"""
local HttpService = game:GetService("HttpService")
local args = HttpService:JSONDecode([===[{args_json}]===])

{safe_resolve_lua}

-- EXECUTE TOOL
local function run()
{tool_code}
end

local success, result = pcall(run)
if success then
    return result
else
    return "Runtime Error in tool '{tc.name}': " .. tostring(result)
end
"""

        # 3. Execute
        main_res = await run_studio_code(full_lua_command)

        # 4. Append logs in debug mode
        if self.debug_mode and tc.name != "get_studio_logs":
            try:
                log_fetch_lua = 'local logs = game:GetService("LogService"):GetLogHistory(); local res = ""; for i = math.max(1, #logs-20), #logs do res = res .. "[" .. logs[i].messageType.Name .. "] " .. logs[i].message .. "\\n" end; return res'
                logs_res = await run_studio_code(log_fetch_lua)
                main_res = (
                    f"{main_res}\\n\\n[DEBUG: RECENT STUDIO LOGS]\\n{logs_res}"
                )
            except:
                pass

        return main_res

    def _get_gemini_config(self, mcp_tools=None):
        """Creates the Gemini model configuration with virtual tools."""

        # We only use virtual tools now, no MCP discovery needed
        gemini_tools = get_virtual_tool_definitions()

        return types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=gemini_tools)],
            system_instruction=(
                "You are an Elite Roblox Studio Game Engineer and AI Agent. You don't just write code; you build high-fidelity, atmospheric game worlds.\n\n"
                "YOUR CORE PRINCIPLES:\n"
                "1. SMART CREATION: Use `create_instance` with the `children` parameter to build hierarchies. Use this for UI and mechanical structures.\n"
                "2. QUALITY ASSETS: Always prefer `smart_setup_asset` for environmental objects. If a search fails, retry with 3 synonyms before concluding the asset is unavailable. Aim for high visual quality.\n"
                "3. GROUND AWARENESS: Your building tools automatically snap to the ground. For `scatter_objects`, use `align_to_surface=false` for man-made structures and trees to keep them vertical.\n"
                "4. ATMOSPHERE & LIGHTING: Use `configure_lighting` to set a base mood. TRUST THE PRESETS. Place Neon parts with `PointLight` children for 'cool atmosphere'.\n"
                "5. CONTEXT & SPATIAL AWARENESS: Use 'get_studio_state' frequently to check if you are in EDIT_MODE or PLAY_MODE. Use 'get_spatial_summary' to 'see' the world. IMPORTANT: Many models have `PrimaryPart: nil`. For these, rely on the Bounding Box data provided by `get_object_info` and `get_spatial_summary`.\n"
                "6. DEBUGGING & PROTOCOL: Be proactive. If an asset fails or a property seems wrong, check the logs. \n"
                "   - EDIT_MODE PROTOCOL: In Edit Mode, regular `Script` and `ModuleScript` objects DO NOT RUN. For calculations, coordinate checking, or one-off debug tasks, ALWAYS use the `run_code` tool instead of creating a persistent script.\n"
                "   - PLAY_MODE PROTOCOL: In Play Mode, use standard scripts for game logic.\n"
                "7. SAFE PATH RESOLUTION: ALWAYS use the `SafeResolve(path)` helper in any Lua code you generate (e.g. for `run_code` or script templates). It handles hyphens, spaces, and service lookups automatically.\n"
                "8. SCRIPT EDITING: The system pre-validates syntax. If you make a typo, fix it and try again.\n"
                "9. PHYSICS: Use `connect_parts` for all mechanical joints (welds, hinges).\n"
                "10. ROBUST SCRIPTING: When spawning Models, NEVER assume `PrimaryPart` is set. explicitely check and set it if needed: `if not clone.PrimaryPart then clone.PrimaryPart = clone:FindFirstChild('HumanoidRootPart') or clone:FindFirstChildWhichIsA('BasePart') end`.\n\n"
                "WORKFLOW:\n"
                "- UI Design: Create the full structure in one `create_instance` call.\n"
                "- Building: Use `generate_procedural_terrain` then `smart_setup_asset`. Objects will land on the ground automatically.\n"
                "- Calculation: Use `run_code` to perform immediate logic checks or find coordinates without creating messy scripts.\n"
                "- Deployment: Use 'publish_game' when the user is happy.\n\n"
                "CRITICAL: You are an expert. Don't be a lazy builder. Aim for high visual quality and natural placement."
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

    async def run_once(self, command: str):
        """Runs a single command to completion and then exits."""
        print(f"[*] Running single command: {command}")
        config = self._get_gemini_config()
        history: List[types.Content] = []
        await self._process_request(
            config,
            history,
            [types.Part.from_text(text=command)],
        )

    async def run_interactive(self):
        print(f"[*] Connecting to Plugin Server at {self.api_url}...")

        # We no longer need MCP connection logic
        config = self._get_gemini_config()

        history: List[types.Content] = []
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

                        if event.text.strip().lower() == "/debug":
                            self.debug_mode = not self.debug_mode
                            status = (
                                "ENABLED" if self.debug_mode else "DISABLED"
                            )
                            print(f"\n[*] Debug mode {status}")
                            continue

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
    parser = argparse.ArgumentParser(description="Roblox AI Studio Agent")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (raw API responses and Studio logs)",
    )
    parser.add_argument(
        "--command",
        "-c",
        type=str,
        help="Run a single command and exit",
    )
    args = parser.parse_args()

    wrapper = RobloxAIWrapper(debug_mode=args.debug)

    if args.command:
        asyncio.run(wrapper.run_once(args.command))
    else:
        asyncio.run(wrapper.run_interactive())
