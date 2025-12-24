# Roblox AI Vibe Coder 🚀

Roblox AI Vibe Coder is an elite integration between **Roblox Studio** and **Google Gemini**, powered by the **Model Context Protocol (MCP)**. It turns the AI from a simple code generator into a proactive, "ground-aware" game engineer that can live-build, debug, and manipulate your Roblox worlds in real-time.

## 🌟 Key Features

- **Proactive Engineering**: The agent doesn't just suggest code; it applies fixes, inspects logs, and verifies its own changes immediately.
- **Ground-Aware Building**: Integrated spatial logic ensures that spawned objects, NPCs, and assets automatically snap to the terrain surface.
- **Rich Toolset**:
  - **Hierarchy Inspection**: Deep-dive into any Service tree.
  - **Scripting Excellence**: Source reading, overwriting, and Cursor-style patching.
  - **Real-time Debugging**: Instant access to Studio logs and error detection with automatic log fetching on failure.
  - **World Manipulation**: Bulk property editing, terrain generation, and procedural scattering.
  - **Smart Asset Integration**: Search and setup marketplace items (weapons, NPCs, props) with one command.
- **Gemini Thinking Support**: Leverages Gemini's reasoning capabilities to plan complex multi-step operations before execution.

## 🏗️ Architecture

The project consists of three main layers:

1.  **Python Wrapper (`roblox_ai.py`)**: The brain. It manages the Gemini session, connects to the MCP server, and translates AI intent into Lua commands.
2.  **Virtual Tool Layer (`tools/`)**: Definitions and Lua templates that map high-level AI actions (like `generate_procedural_terrain`) to optimized Luau execution.
3.  **Roblox Studio MCP Server**: A binary (e.g., `rbx-studio-mcp`) that acts as a bridge, receiving Luau code from the Python wrapper and executing it directly inside the active Studio session.

## 🚀 Getting Started

### Prerequisites

1.  **Roblox Studio MCP**: You must have the Roblox Studio MCP bridge installed and running.
    - Default path expected: `/Applications/RobloxStudioMCP.app/Contents/MacOS/rbx-studio-mcp`
2.  **Google Gemini API Key**: Obtain a key from [Google AI Studio](https://aistudio.google.com/).
3.  **Python 3.10+**: Managed via `uv` or `pip`.

### Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/roblox-ai-vibe-coder.git
cd roblox-ai-vibe-coder

# Install dependencies
uv sync
```

### Configuration

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_api_key_here
```

### Running the Agent

Start the interactive session:

```bash
uv run roblox_ai.py
```

Once connected, you can talk to the agent in natural language:
- *"Generate a rolling hills landscape with a small village near the spawn."*
- *"Debug why my zombie NPC isn't moving."*
- *"Find all scripts that reference 'GoldValue' and update them to use the new 'Currency' module."*
- *"Style all parts in Workspace named 'Wall' to be semi-transparent and red."*

## 🛠️ Tooling Summary

| Tool | Description |
| :--- | :--- |
| `inspect_service` | Tree view of any Roblox service hierarchy. |
| `read/edit/patch_script` | Full suite of script management tools. |
| `get_studio_logs` | Fetch recent Output window logs (essential for debugging). |
| `generate_procedural_terrain` | Noise-based terrain generation (Hills, Plains, etc.). |
| `smart_setup_asset` | Search, insert, and auto-place Marketplace assets. |
| `modify_instance` | Bulk property updates in a single turn. |
| `create_timed_spawner` | Automated object spawning system. |

---

## ⚠️ Important Notes

- **Edit vs. Play Mode**: Some actions (like spawning objects via script) behave differently in Play Mode. Use `get_studio_state` to check the environment.
- **Publishing**: The `publish_game` tool is included but will always require manual confirmation for safety.
- **Engine Security**: Certain properties (like `Technology`) cannot be set via script due to Roblox engine restrictions.

---
*Built for engineers who value simplicity, robustness, and the "vibe" of building.*

