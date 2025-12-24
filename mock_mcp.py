import sys
import json
import asyncio


async def main():
    # Helper to send JSON messages
    def send(data):
        sys.stdout.write(json.dumps(data) + "\n")
        sys.stdout.flush()

    # 1. Handle initialize
    line = await asyncio.get_event_loop().run_in_executor(
        None, sys.stdin.readline
    )
    if not line:
        return
    req = json.loads(line)
    send(
        {
            "jsonrpc": "2.0",
            "id": req["id"],
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "mock-roblox", "version": "1.0.0"},
            },
        }
    )

    # 2. Handle initialized notification (no response needed)
    line = await asyncio.get_event_loop().run_in_executor(
        None, sys.stdin.readline
    )

    # 3. Main loop
    while True:
        line = await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline
        )
        if not line:
            break
        req = json.loads(line)

        if req["method"] == "tools/list":
            send(
                {
                    "jsonrpc": "2.0",
                    "id": req["id"],
                    "result": {
                        "tools": [
                            {
                                "name": "run_code",
                                "description": "Run Luau code in Studio",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "command": {"type": "string"}
                                    },
                                    "required": ["command"],
                                },
                            },
                            {
                                "name": "insert_model",
                                "description": "Insert a model from the Toolbox",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "modelId": {"type": "number"}
                                    },
                                    "required": ["modelId"],
                                },
                            },
                        ]
                    },
                }
            )
        elif req["method"] == "tools/call":
            send(
                {
                    "jsonrpc": "2.0",
                    "id": req["id"],
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": "Successfully executed in mock Studio.",
                            }
                        ],
                        "isError": False,
                    },
                }
            )
        else:
            send({"jsonrpc": "2.0", "id": req["id"], "result": {}})


if __name__ == "__main__":
    asyncio.run(main())
