# Roblox AI Vibe Coder 🚀

Roblox AI Vibe Coder is an elite integration between **Roblox Studio** and **Google Gemini**. It turns the AI from a simple code generator into a proactive, "ground-aware" game engineer that can live-build, debug, and manipulate your Roblox worlds in real-time.

## 🌟 Key Features

- **Proactive Engineering**: The agent doesn't just suggest code; it applies fixes, inspects logs, and verifies its own changes immediately.
- **Voice-Powered Interaction (PTT)**: Hold the **Right Command** key to speak directly to the agent.
- **Instant Interruption**: Don't wait for the agent to finish; you can interrupt a thinking loop or a tool execution at any time by speaking.
- **Ground-Aware Building**: Integrated spatial logic ensures that spawned objects, NPCs, and assets automatically snap to the terrain surface.
- **Polling Architecture**: No complex binary bridges required. Uses a lightweight Roblox Studio plugin and a local FastAPI server.
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

The project uses a **Local Bridge Architecture** to communicate with Roblox Studio:

1.  **Orchestrator (`roblox_ai.py`)**: The brain. It handles user input (text/voice), manages the Gemini session, converts tool calls into Lua, and pushes them to the Bridge Server.
2.  **Bridge Server (`server.py`)**: A FastAPI-powered middleman that manages a command queue and stores execution results.
3.  **Roblox Plugin (`plugin/Main.lua`)**: A Lua plugin running inside Roblox Studio that polls the Bridge Server for new commands and executes them in real-time.

## 🚀 Getting Started

### Prerequisites

1.  **Google Gemini API Key**: Obtain a key from [Google AI Studio](https://aistudio.google.com/).
2.  **Python 3.11+**: Required for `asyncio.TaskGroup` and structured concurrency.
3.  **Roblox Studio**: With "Allow HTTP Requests" enabled in Game Settings.

### Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/roblox-ai-vibe-coder.git
cd roblox-ai-vibe-coder

# Install dependencies
uv sync
```

### Configuration

1. Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

2. **Install the Roblox Plugin**:
   - Copy the contents of `plugin/Main.lua` into a new **Local Plugin** in Roblox Studio.
   - Alternatively, drag the `plugin` folder into the `Plugins` directory of your Roblox installation.

### Running the Agent

You need to run two components:

1.  **Start the Bridge Server**:
    ```bash
    uv run server.py
    ```

2.  **Start the Orchestrator**:
    ```bash
    uv run roblox_ai.py
    ```

3.  **In Roblox Studio**:
    - Click the **"Connect"** button in the "Vibe Coder" toolbar.

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
