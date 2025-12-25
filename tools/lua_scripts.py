import os

# Get the absolute path to the directory containing this script
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_LUA_DIR = os.path.join(_CURRENT_DIR, "lua")


def _load_script(filename):
    """Loads a Lua script from the tools/lua directory."""
    try:
        with open(os.path.join(_LUA_DIR, filename), "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Lua script '{filename}' not found in {_LUA_DIR}")
        return ""


# Load scripts on module import
INSPECT_SERVICE_LUA = _load_script("inspect_service.lua")
READ_SCRIPT_LUA = _load_script("read_script.lua")
EDIT_SCRIPT_LUA = _load_script("edit_script.lua")
PATCH_SCRIPT_LUA = _load_script("patch_script.lua")
GET_LOGS_LUA = _load_script("get_logs.lua")
CLEAR_LOGS_LUA = _load_script("clear_logs.lua")
SEARCH_SCRIPTS_LUA = _load_script("search_scripts.lua")
GET_OBJECT_INFO_LUA = _load_script("get_object_info.lua")
SEARCH_MARKETPLACE_LUA = _load_script("search_marketplace.lua")
MANAGE_TAGS_LUA = _load_script("manage_tags.lua")
RUN_TESTS_LUA = _load_script("run_tests.lua")
GET_STATS_LUA = _load_script("get_stats.lua")
GET_PROPERTIES_LUA = _load_script("get_properties.lua")
SET_PROPERTY_LUA = _load_script("set_property.lua")
FIND_INSTANCES_LUA = _load_script("find_instances.lua")
CREATE_INSTANCE_LUA = _load_script("create_instance.lua")
DELETE_INSTANCE_LUA = _load_script("delete_instance.lua")
RAYCAST_LUA = _load_script("raycast.lua")
INSERT_ASSET_LUA = _load_script("insert_asset.lua")
PUBLISH_GAME_LUA = _load_script("publish_game.lua")
MODIFY_INSTANCE_LUA = _load_script("modify_instance.lua")
GET_STUDIO_STATE_LUA = _load_script("get_studio_state.lua")
MANIPULATE_TERRAIN_LUA = _load_script("manipulate_terrain.lua")
GENERATE_TERRAIN_LUA = _load_script("generate_terrain.lua")
SMART_SETUP_LUA = _load_script("smart_setup.lua")
SCATTER_LUA = _load_script("scatter.lua")
REPARENT_INSTANCE_LUA = _load_script("reparent_instance.lua")
CREATE_SPAWNER_LUA = _load_script("create_spawner.lua")
GET_SPATIAL_SUMMARY_LUA = _load_script("get_spatial_summary.lua")
CONNECT_PARTS_LUA = _load_script("connect_parts.lua")
