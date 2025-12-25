import asyncio
import os
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn
import uuid
import json

from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import your existing tools
from tools.definitions import get_virtual_tool_definitions

# Load Env
load_dotenv()


# --- DATA MODELS ---
class CommandRequest(BaseModel):
    text: str
    user_id: str = "default_user"


class PollRequest(BaseModel):
    status: str
    place_id: Optional[int] = None


class CallbackRequest(BaseModel):
    id: str
    result: Any


# --- STATE MANAGEMENT ---
# In a real app, use Redis. For now, memory is fine.
class ConnectionManager:
    def __init__(self):
        # Pending Lua commands waiting for the plugin to pick them up
        # { "user_id": [ { "id": "123", "code": "..." } ] }
        self.command_queues: Dict[str, List[Dict[str, Any]]] = {}

        # Results from the plugin
        # { "cmd_id": "Success: Part created" }
        self.results: Dict[str, Any] = {}

    def queue_command(self, user_id: str, code: str):
        if user_id not in self.command_queues:
            self.command_queues[user_id] = []

        cmd_id = str(uuid.uuid4())
        cmd = {"id": cmd_id, "code": code}
        self.command_queues[user_id].append(cmd)
        return cmd_id

    def get_next_command(self, user_id: str):
        if user_id in self.command_queues and self.command_queues[user_id]:
            return self.command_queues[user_id].pop(0)
        return None

    def store_result(self, cmd_id: str, result: Any):
        self.results[cmd_id] = result

    async def wait_for_result(self, cmd_id: str, timeout: int = 10):
        for _ in range(timeout * 2):  # Check every 0.5s
            if cmd_id in self.results:
                return self.results.pop(cmd_id)
            await asyncio.sleep(0.5)
        return "Timeout: Plugin did not respond."


manager = ConnectionManager()


# --- AI LOGIC (Mini Wrapper) ---
class CloudBrain:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(api_version="v1beta"),
        )
        self.model_id = "gemini-2.0-flash-exp"

    async def process_and_queue(self, text: str, user_id: str):
        print(f"[Brain] Thinking about: {text}")

        # 1. Ask Gemini to generate tool calls
        config = types.GenerateContentConfig(
            tools=[
                types.Tool(function_declarations=get_virtual_tool_definitions())
            ],
        )

        response = await self.client.aio.models.generate_content(
            model=self.model_id,
            contents=[
                types.Content(
                    role="user", parts=[types.Part.from_text(text=text)]
                )
            ],
            config=config,
        )

        results = []

        # 2. Extract Tool Calls -> Convert to Lua -> Queue
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    fc = part.function_call
                    print(f"[Brain] Tool Call: {fc.name}")

                    # Convert the Tool Call to Lua Code using your existing templates
                    # For MVP, we will just queue a simple print, but you should link this
                    # to your 'roblox_ai.py' logic later.

                    # HACK: For now, I will interpret the tool call loosely
                    # In the real version, you import your _handle_tool_call logic
                    lua_code = self._convert_tool_to_lua(fc.name, fc.args)

                    if lua_code:
                        cmd_id = manager.queue_command(user_id, lua_code)
                        # Wait for execution (optional, blocks response)
                        # res = await manager.wait_for_result(cmd_id)
                        results.append(f"Queued {fc.name}")

        return {"status": "ok", "actions": results}

    def _convert_tool_to_lua(self, name, args):
        # This is where you map "create_instance" -> "CREATE_INSTANCE_LUA.format(...)"
        # reusing your tools/lua_scripts.py templates
        from tools.lua_scripts import CREATE_INSTANCE_LUA, GENERATE_TERRAIN_LUA

        # Simple Example Mapping
        if name == "create_instance":
            # Basic conversion (incomplete, just for demo)
            return f'Instance.new("{args.get("class_name")}", workspace).Name = "{args.get("name", "AI_Part")}"'

        if name == "generate_procedural_terrain":
            return f'print("Generating terrain at {args.get("position")}...")'

        # Fallback for testing
        return f'print("AI executed tool: {name}")'


brain = CloudBrain()

# --- API ROUTES ---
app = FastAPI()


@app.get("/")
def home():
    return {"message": "Vibe Coder Cloud is Running"}


class QueueRequest(BaseModel):
    user_id: str
    code: str


@app.post("/queue")
def queue_code(req: QueueRequest):
    """Internal endpoint for the Brain to push Lua code directly"""
    cmd_id = manager.queue_command(req.user_id, req.code)
    return {"id": cmd_id, "status": "queued"}


@app.post("/command")
async def user_command(req: CommandRequest):
    """Web UI sends text here"""
    res = await brain.process_and_queue(req.text, req.user_id)
    return res


@app.post("/poll")
def plugin_poll(req: PollRequest):
    """Roblox Plugin asks for work here"""
    # In MVP, we assume single user. In prod, map req.place_id to user.
    user_id = "default_user"

    cmd = manager.get_next_command(user_id)
    if cmd:
        return {"command": cmd}
    return {"command": None}


@app.get("/result/{cmd_id}")
def get_result(cmd_id: str):
    """Poll for the result of a specific command"""
    if cmd_id in manager.results:
        return {"status": "completed", "result": manager.results[cmd_id]}
    return {"status": "pending"}


@app.post("/callback")
def plugin_callback(req: CallbackRequest):
    """Plugin reports success/fail"""
    print(f"[Plugin] Callback {req.id}: {req.result}")
    manager.store_result(req.id, req.result)
    return {"status": "received"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
