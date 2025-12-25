# Roblox AI Vibe Coder 🚀

Roblox AI Vibe Coder is an elite integration between **Roblox Studio** and **Google Gemini**, powered by the **Model Context Protocol (MCP)**. It turns the AI from a simple code generator into a proactive, "ground-aware" game engineer that can live-build, debug, and manipulate your Roblox worlds in real-time.

## 🌟 Key Features

- **Proactive Engineering**: The agent doesn't just suggest code; it applies fixes, inspects logs, and verifies its own changes immediately.
- **Voice-Powered Interaction (PTT)**: Hold the **Right Command** key to speak directly to the agent.
- **Instant Interruption**: Don't wait for the agent to finish; you can interrupt a thinking loop or a tool execution at any time by speaking.
- **Ground-Aware Building**: Integrated spatial logic ensures that spawned objects, NPCs, and assets automatically snap to the terrain surface.
- **Rich Toolset**:
  - **Hierarchy Inspection**: Deep-dive into any Service tree.
  - **Scripting Excellence**: Source reading, overwriting, and Cursor-style patching.
  - **Real-time Debugging**: Instant access to Studio logs and error detection with automatic log fetching on failure.
  - **World Manipulation**: Bulk property editing, terrain generation, and procedural scattering.
  - **Smart Asset Integration**: Search and setup marketplace items (weapons, NPCs, props) with one command.
  - **System Architecture**: High-fidelity tools for UI generation, Lighting presets, and robust Game Logic patterns.
  - **Mechanical Engineering**: Construct vehicles and machines using constraints (Welds, Hinges, Motors) with `connect_parts`.
  - **Quality Assurance**: Built-in unit testing runner (`run_unit_tests`) and performance monitoring (`get_performance_stats`).
  - **Codebase Navigation**: Instantly find logic across all scripts with `search_scripts`.
  - **Gemini Thinking Support**: Leverages Gemini's reasoning capabilities to plan complex multi-step operations before execution.

## 🏗️ Architecture

The project consists of three main layers:

1.  **Orchestrator (`roblox_ai.py`)**: An event-driven brain built with Python 3.11's `asyncio.TaskGroup`. It manages a central event queue for text and voice, handling real-time interruptions and Gemini 3 Flash multimodal sessions.
2.  **Virtual Tool Layer (`tools/`)**: Definitions and Lua templates that map high-level AI actions (like `generate_procedural_terrain`) to optimized Luau execution.
3.  **Roblox Studio MCP Server**: A binary (e.g., `rbx-studio-mcp`) that acts as a bridge, receiving Luau code from the orchestrator and executing it directly inside the active Studio session.

## 🚀 Getting Started

### Prerequisites

1.  **Roblox Studio MCP**: You must have the Roblox Studio MCP bridge installed and running.
    - Default path expected: `/Applications/RobloxStudioMCP.app/Contents/MacOS/rbx-studio-mcp`
2.  **Google Gemini API Key**: Obtain a key from [Google AI Studio](https://aistudio.google.com/).
3.  **Python 3.11+**: Required for `asyncio.TaskGroup` and structured concurrency.

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

**How to interact:**
- **Type**: Enter commands normally at the `> ` prompt.
- **Speak**: HOLD the **Right Command** key, speak your instruction, and release to send.
- **Interrupt**: Press **Right Command** at any time to cancel the agent's current task and start a new voice command.

Once connected, you can talk to the agent:
- *"Generate a rolling hills landscape with a small village near the spawn."*
- *"Debug why my zombie NPC isn't moving."*
- *"Find all scripts that reference 'GoldValue' and update them to use the new 'Currency' module."*
- *"Style all parts in Workspace named 'Wall' to be semi-transparent and red."*

## 🛠️ Tooling Summary

### 🌍 World & Environment
| Tool | Description |
| :--- | :--- |
| `generate_procedural_terrain` | Noise-based terrain generation (Hills, Plains, etc.). |
| `manipulate_terrain` | Precision terrain editing (Fill Block/Ball, Subtract). |
| `scatter_objects` | Procedurally scatter assets with surface alignment. |
| `configure_lighting` | One-click professional lighting presets (Day, Night, Horror). |
| `raycast_check` | Debug physics and line-of-sight. |
| `get_spatial_summary` | AI vision of the immediate surroundings. |

### 🧱 Building & Assets
| Tool | Description |
| :--- | :--- |
| `smart_setup_asset` | Search, insert, and auto-place Marketplace assets. |
| `search_marketplace` | Query the Roblox library for asset IDs. |
| `create_timed_spawner` | Automated object spawning system. |
| `connect_parts` | Create mechanical constraints (Welds, Motors, Hinges). |
| `modify_instance` | Bulk property updates for styling. |
| `reparent_instance` | Move objects (e.g., equip tools/scripts). |
| `create_instance` | Recursive instance creation (great for custom trees). |

### 💻 Scripting & Logic
| Tool | Description |
| :--- | :--- |
| `read/edit/patch_script` | Full suite of script management tools. |
| `inject_script_template` | Inject standard game patterns (Leaderstats, Doors). |
| `search_scripts` | Find code across the entire project. |
| `run_unit_tests` | Execute .spec verification scripts. |
| `create_ui_layout` | Generate responsive UI hierarchies. |

### 🔍 Debugging & Inspection
| Tool | Description |
| :--- | :--- |
| `inspect_service` | Tree view of hierarchy and attributes. |
| `get_studio_logs` | Fetch real-time Output window logs. |
| `get_object_info` | Detailed property and tag inspection. |
| `find_instances` | Search for objects by Name or ClassName. |
| `get_performance_stats` | Monitor Memory, FPS, and Primitives. |
| `manage_tags` | CollectionService tag management. |

---

## ⚠️ Important Notes

- **Edit vs. Play Mode**: Some actions (like spawning objects via script) behave differently in Play Mode. Use `get_studio_state` to check the environment.
- **Publishing**: The `publish_game` tool is included but will always require manual confirmation for safety.
- **Engine Security**: Certain properties (like `Technology`) cannot be set via script due to Roblox engine restrictions.

---
*Built for engineers who value simplicity, robustness, and the "vibe" of building.*

