from google.genai import types


def get_virtual_tool_definitions():
    """Returns the definitions for the virtual tools used by the Roblox AI."""
    return [
        types.FunctionDeclaration(
            name="inspect_service",
            description="Returns a tree view of a Roblox Service. Includes hierarchy, attributes, and model PrimaryParts.",
            parameters={
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "The service to inspect (e.g., 'Workspace', 'ReplicatedStorage').",
                        "default": "Workspace",
                    },
                    "depth": {
                        "type": "integer",
                        "description": "How many levels deep to inspect.",
                        "default": 4,
                    },
                },
            },
        ),
        types.FunctionDeclaration(
            name="read_script_source",
            description="Reads the source code of a script in any service.",
            parameters={
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "The full path to the script (e.g., 'game.ServerScriptService.MyHandler').",
                    }
                },
                "required": ["script_path"],
            },
        ),
        types.FunctionDeclaration(
            name="edit_script_source",
            description="Overwrites the source code of an existing script in the project.",
            parameters={
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "The full path to the script.",
                    },
                    "new_source": {
                        "type": "string",
                        "description": "The complete new source code for the script.",
                    },
                },
                "required": ["script_path", "new_source"],
            },
        ),
        types.FunctionDeclaration(
            name="patch_script_source",
            description="Modifies a specific part of a script without overwriting the entire file (Cursor-style patching).",
            parameters={
                "type": "object",
                "properties": {
                    "script_path": {
                        "type": "string",
                        "description": "The full path to the script.",
                    },
                    "search_string": {
                        "type": "string",
                        "description": "The exact string or function block to replace.",
                    },
                    "replace_string": {
                        "type": "string",
                        "description": "The new code to insert instead.",
                    },
                },
                "required": ["script_path", "search_string", "replace_string"],
            },
        ),
        types.FunctionDeclaration(
            name="get_studio_logs",
            description="Fetches recent logs/errors from Studio. USE THIS TO DEBUG CRASHES.",
            parameters={
                "type": "object",
                "properties": {
                    "line_count": {
                        "type": "integer",
                        "description": "Number of recent log lines to fetch.",
                        "default": 50,
                    }
                },
            },
        ),
        types.FunctionDeclaration(
            name="clear_studio_logs",
            description="Prints a separator in the logs to mark the start of a new debug session. USE THIS BEFORE TESTING A FIX.",
            parameters={"type": "object", "properties": {}},
        ),
        types.FunctionDeclaration(
            name="search_scripts",
            description="Searches all scripts for a string or Lua pattern. USE THIS TO FIND LOGIC.",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The string or Lua pattern to search for (e.g., 'SpawnUnit', 'Gold%%.Value').",
                    }
                },
                "required": ["pattern"],
            },
        ),
        types.FunctionDeclaration(
            name="get_object_info",
            description="Returns detailed info about an object (properties, attributes, tags).",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The full path to the object.",
                    }
                },
                "required": ["path"],
            },
        ),
        types.FunctionDeclaration(
            name="find_script_references",
            description="Finds all scripts that reference or require a specific module/variable.",
            parameters={
                "type": "object",
                "properties": {
                    "target_name": {
                        "type": "string",
                        "description": "The name of the module or variable to find references for.",
                    }
                },
                "required": ["target_name"],
            },
        ),
        types.FunctionDeclaration(
            name="manage_tags",
            description="Adds, removes, or lists objects with a specific CollectionService tag.",
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["add", "remove", "get"],
                        "description": "The action to perform.",
                    },
                    "tag": {
                        "type": "string",
                        "description": "The tag name.",
                    },
                    "path": {
                        "type": "string",
                        "description": "The path to the object (required for add/remove).",
                    },
                },
                "required": ["action", "tag"],
            },
        ),
        types.FunctionDeclaration(
            name="run_unit_tests",
            description="Runs all script specs (ending in .spec) in the project and reports pass/fail.",
            parameters={"type": "object", "properties": {}},
        ),
        types.FunctionDeclaration(
            name="get_performance_stats",
            description="Fetches performance metrics (Memory, FPS, Instances) from Roblox Studio.",
            parameters={"type": "object", "properties": {}},
        ),
        types.FunctionDeclaration(
            name="get_properties",
            description="Returns all public properties of an instance. Handles Vector3, CFrame, etc. correctly.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The full path to the instance (e.g., 'game.Workspace.Part').",
                    }
                },
                "required": ["path"],
            },
        ),
        types.FunctionDeclaration(
            name="set_property",
            description="Sets a property on a Roblox instance. Supports strings, numbers, booleans, and Vector3/Color3 (as tables or strings).",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The full path to the instance.",
                    },
                    "property": {
                        "type": "string",
                        "description": "The name of the property to set (e.g., 'Anchored', 'Transparency', 'Size').",
                    },
                    "value": {
                        "type": "string",
                        "description": "The value to set. For Vector3 use 'x,y,z', for Color3 use 'r,g,b' or hex.",
                    },
                },
                "required": ["path", "property", "value"],
            },
        ),
        types.FunctionDeclaration(
            name="find_instances",
            description="Searches for instances matching specific criteria (ClassName, Name, or Property values).",
            parameters={
                "type": "object",
                "properties": {
                    "root_path": {
                        "type": "string",
                        "description": "Where to start the search (e.g., 'game.Workspace').",
                        "default": "game",
                    },
                    "class_name": {
                        "type": "string",
                        "description": "Filter by ClassName (e.g., 'Part', 'Script').",
                    },
                    "name_pattern": {
                        "type": "string",
                        "description": "Filter by Name (Lua pattern).",
                    },
                },
            },
        ),
        types.FunctionDeclaration(
            name="create_instance",
            description="Creates a new instance of a class, sets its properties, and parents it. Use this to create and style in ONE turn.",
            parameters={
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "The class to create (e.g., 'Part', 'Folder', 'ModuleScript').",
                    },
                    "parent_path": {
                        "type": "string",
                        "description": "Where to parent the new instance.",
                    },
                    "name": {
                        "type": "string",
                        "description": "The name of the new instance.",
                    },
                    "properties": {
                        "type": "object",
                        "description": "Optional dictionary of properties to set immediately (e.g., {'Anchored': true, 'Transparency': 0.5}).",
                    },
                },
                "required": ["class_name", "parent_path"],
            },
        ),
        types.FunctionDeclaration(
            name="delete_instance",
            description="Deletes an instance from the game.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The full path to the instance to delete.",
                    }
                },
                "required": ["path"],
            },
        ),
        types.FunctionDeclaration(
            name="raycast_check",
            description="Performs a raycast to check for ground or obstacles. Useful for debugging character movement.",
            parameters={
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "The origin point 'x,y,z'.",
                    },
                    "direction": {
                        "type": "string",
                        "description": "The direction vector 'x,y,z'.",
                    },
                },
                "required": ["origin", "direction"],
            },
        ),
        types.FunctionDeclaration(
            name="publish_game",
            description="PUBLISHES THE GAME TO ROBLOX CLOUD. This makes the game playable on Xbox/Mobile. This tool is special and will always ask the user for manual confirmation before running.",
            parameters={"type": "object", "properties": {}},
        ),
        types.FunctionDeclaration(
            name="modify_instance",
            description="Sets multiple properties on a Roblox instance at once. Efficient for bulk styling (Color, Size, Transparency, etc.).",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The full path to the instance.",
                    },
                    "properties": {
                        "type": "object",
                        "description": "A dictionary of property names and values to set.",
                    },
                },
                "required": ["path", "properties"],
            },
        ),
        types.FunctionDeclaration(
            name="get_studio_state",
            description="Returns the current state of Roblox Studio (Edit Mode vs Play Mode). Use this to check if scripts are running or if you are just in the editor.",
            parameters={"type": "object", "properties": {}},
        ),
        types.FunctionDeclaration(
            name="manipulate_terrain",
            description="Manipulates Roblox Terrain (adds/removes material). Use this to create hills, valleys, or caves.",
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["fillBlock", "fillBall", "fillCylinder"],
                        "description": "The shape to fill (e.g., 'fillBlock' for plateaus, 'fillBall' for hills).",
                    },
                    "position": {
                        "type": "string",
                        "description": "The center position 'x,y,z'.",
                    },
                    "size": {
                        "type": "string",
                        "description": "The size. For fillBlock: 'x,y,z'. For fillBall: 'radius'. For fillCylinder: 'radius,height'.",
                    },
                    "material": {
                        "type": "string",
                        "description": "The Terrain material (e.g., 'Grass', 'Rock', 'Water', 'Air'). Use 'Air' to delete terrain.",
                        "default": "Grass",
                    },
                },
                "required": ["action", "position", "size"],
            },
        ),
        types.FunctionDeclaration(
            name="generate_procedural_terrain",
            description="Generates a large area of procedural terrain using noise. Best for creating base maps.",
            parameters={
                "type": "object",
                "properties": {
                    "position": {
                        "type": "string",
                        "description": "Center position 'x,y,z'.",
                    },
                    "size": {
                        "type": "string",
                        "description": "Area size 'width,depth'.",
                    },
                    "scale": {
                        "type": "number",
                        "description": "Noise scale (higher = smoother hills, lower = jagged).",
                        "default": 100,
                    },
                    "amplitude": {
                        "type": "number",
                        "description": "Max height of hills.",
                        "default": 50,
                    },
                    "material": {
                        "type": "string",
                        "description": "Base material.",
                        "default": "Grass",
                    },
                    "biome": {
                        "type": "string",
                        "enum": ["hills", "mountains", "plains", "craters"],
                        "description": "The type of terrain to generate.",
                        "default": "hills",
                    },
                },
                "required": ["position", "size"],
            },
        ),
        types.FunctionDeclaration(
            name="smart_setup_asset",
            description="Searches, inserts, and automatically sets up an asset (e.g., weapon or NPC). Moves Tools to StarterPack and NPCs to ServerStorage.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Marketplace search query (e.g., 'Zombie', 'Shotgun').",
                    },
                    "position": {
                        "type": "string",
                        "description": "Optional 'x,y,z' to place the asset at.",
                        "default": "0,5,0",
                    },
                },
                "required": ["query"],
            },
        ),
        types.FunctionDeclaration(
            name="scatter_objects",
            description="Scatters multiple clones of an object across an area with ground detection.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Full path to the source object (e.g., 'game.Workspace.Tree').",
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of objects to scatter.",
                        "default": 10,
                    },
                    "radius": {
                        "type": "number",
                        "description": "The radius of the scattering area.",
                        "default": 100,
                    },
                },
                "required": ["path"],
            },
        ),
        types.FunctionDeclaration(
            name="inspect_marketplace_item",
            description="Returns detailed metadata (description, tags, creator) and a summary of contents (class counts) for a marketplace item before permanent insertion.",
            parameters={
                "type": "object",
                "properties": {
                    "asset_id": {
                        "type": "integer",
                        "description": "The ID of the marketplace asset.",
                    }
                },
                "required": ["asset_id"],
            },
        ),
        types.FunctionDeclaration(
            name="create_timed_spawner",
            description="Creates a script that automatically spawns clones of a template object at regular intervals within a specific area.",
            parameters={
                "type": "object",
                "properties": {
                    "template_path": {
                        "type": "string",
                        "description": "Path to the object to clone (e.g., 'game.ServerStorage.NPC').",
                    },
                    "container_name": {
                        "type": "string",
                        "description": "Name of the folder where spawned objects will be placed.",
                        "default": "SpawnedObjects",
                    },
                    "interval": {
                        "type": "number",
                        "description": "Seconds between spawns.",
                        "default": 5,
                    },
                    "max_count": {
                        "type": "integer",
                        "description": "Maximum number of active spawned objects allowed.",
                        "default": 10,
                    },
                    "spawn_area_center": {
                        "type": "string",
                        "description": "Center of spawn area 'x,y,z'.",
                        "default": "0,10,0",
                    },
                    "spawn_radius": {
                        "type": "number",
                        "description": "Radius from center to spawn within.",
                        "default": 100,
                    },
                },
                "required": ["template_path"],
            },
        ),
    ]
