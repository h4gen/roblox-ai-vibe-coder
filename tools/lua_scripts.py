# Lua scripts for Roblox Studio virtual tools

INSPECT_SERVICE_LUA = """
local function getHierarchy(obj, depth, maxDepth)
    if depth > maxDepth then return "" end
    local meta = " [" .. obj.ClassName .. "]"
    if obj:IsA("Model") and obj.PrimaryPart then meta = meta .. " [PP:" .. obj.PrimaryPart.Name .. "]" end
    
    local atts = obj:GetAttributes()
    local attStr = ""
    for k, v in pairs(atts) do
        attStr = attStr .. k .. "=" .. tostring(v) .. ","
    end
    if attStr ~= "" then meta = meta .. " [Attrs:" .. attStr:sub(1, -2) .. "]" end

    local result = obj.Name .. meta .. "\\n"
    for _, child in ipairs(obj:GetChildren()) do
        result = result .. string.rep("  ", depth + 1) .. getHierarchy(child, depth + 1, maxDepth)
    end
    return result
end
local s = game:GetService("{service}")
if s then print(getHierarchy(s, 0, {depth})) else print("Error: Service '{service}' not found.") end
"""

READ_SCRIPT_LUA = """
local target = {script_path}
if target and (target:IsA("LuaSourceContainer")) then
    print(target.Source)
else
    print("Error: Script at '{script_path}' not found or is not a script container.")
end
"""

EDIT_SCRIPT_LUA = """
local target = {script_path}
if target and (target:IsA("LuaSourceContainer")) then
    target.Source = [===[{new_source}]===]
    print("Successfully updated script: " .. target.Name)
else
    print("Error: Could not find script at path '{script_path}' to edit.")
end
"""

PATCH_SCRIPT_LUA = """
local target = {script_path}
if target and (target:IsA("LuaSourceContainer")) then
    local oldSource = target.Source
    local search = [===[{search_string}]===]
    local replace = [===[{replace_string}]===]
    
    -- Use string.find with 'true' for literal search (no patterns)
    local startIdx, endIdx = string.find(oldSource, search, 1, true)
    if startIdx then
        target.Source = string.sub(oldSource, 1, startIdx - 1) .. replace .. string.sub(oldSource, endIdx + 1)
        print("Successfully patched script: " .. target.Name)
    else
        print("Error: Search string not found in script (literal match failed).")
    end
else
    print("Error: Could not find script at path '{script_path}' to patch.")
end
"""

GET_LOGS_LUA = """
local LogService = game:GetService("LogService")
local logs = LogService:GetLogHistory()
local count = {count}
local startIdx = math.max(1, #logs - count + 1)
local result = "--- Recent Studio Logs ---\\n"
for i = startIdx, #logs do
    local log = logs[i]
    result = result .. "[" .. log.messageType.Name .. "] " .. log.message .. "\\n"
end
print(result)
"""

CLEAR_LOGS_LUA = """
-- Note: There is no direct API to clear the Studio Output window via script,
-- but we can print a separator to help the AI distinguish new sessions.
print("\\n" .. string.rep("=", 50))
print("NEW DEBUG SESSION STARTED")
print(string.rep("=", 50) .. "\\n")
"""

SEARCH_SCRIPTS_LUA = """
local pattern = "{pattern}"
local results = "--- Search Results for '" .. pattern .. "' ---\\n"
local count = 0

local function search(obj)
    if obj:IsA("LuaSourceContainer") then
        if obj.Source:find(pattern) then
            results = results .. obj:GetFullName() .. "\\n"
            count = count + 1
        end
    end
    for _, child in ipairs(obj:GetChildren()) do
        search(child)
    end
end

search(game)
print(results .. "Total found: " .. count)
"""

GET_OBJECT_INFO_LUA = """
local target = {path}
if not target then print("Error: Object not found.") return end

print("--- Info for: " .. target:GetFullName() .. " ---")
print("ClassName: " .. target.ClassName)

if target:IsA("BasePart") then
    print("Size: " .. tostring(target.Size))
    print("Position: " .. tostring(target.Position))
elseif target:IsA("Model") then
    print("ExtentsSize: " .. tostring(target:GetExtentsSize()))
    print("PrimaryPart: " .. tostring(target.PrimaryPart))
end

local atts = target:GetAttributes()
print("Attributes:")
for k, v in pairs(atts) do
    print("  " .. k .. ": " .. tostring(v))
end

local tags = game:GetService("CollectionService"):GetTags(target)
print("Tags: " .. table.concat(tags, ", "))
"""

SEARCH_MARKETPLACE_LUA = """
local InsertService = game:GetService("InsertService")
local query = "{query}"

local success, result = pcall(function()
    return InsertService:GetFreeModels(query, 0)
end)

local output = "--- Marketplace Search Results for '" .. query .. "' ---\\n"

if success then
    if result then
        local pages = result:GetCurrentPage()
        if #pages == 0 then
            print("0 results found for '" .. query .. "'. \\nTIP: Try broader 1-2 word keywords (e.g., 'tombstone' instead of 'spooky mossy graveyard stone').")
        else
            for i = 1, math.min(5, #pages) do
                local item = pages[i]
                output = output .. i .. ". " .. item.Name .. " (Creator: " .. item.CreatorName .. ", AssetID: " .. item.AssetId .. ")\\n"
            end
            print(output)
        end
    else
        print("Error: Marketplace search returned nil result.")
    end
else
    print("Error searching marketplace: " .. tostring(result))
end
"""

FIND_REFS_LUA = """
local targetName = "{target_name}":lower()
local results = "--- References found for '" .. targetName .. "' ---\\n"
local count = 0

local function searchRefs(obj)
    if obj:IsA("LuaSourceContainer") then
        local source = obj.Source:lower()
        if source:find("require%(" .. targetName .. "%)") or source:find(targetName) then
            results = results .. obj:GetFullName() .. "\\n"
            count = count + 1
        end
    end
    for _, child in ipairs(obj:GetChildren()) do
        searchRefs(child)
    end
end

searchRefs(game)
print(results .. "Total references found: " .. count)
"""

MANAGE_TAGS_LUA = """
local CS = game:GetService("CollectionService")
local target = {path}
local action = "{action}"
local tag = "{tag}"

if not target then print("Error: Object not found.") return end

if action == "add" then
    CS:AddTag(target, tag)
    print("Added tag '" .. tag .. "' to " .. target.Name)
elseif action == "remove" then
    CS:RemoveTag(target, tag)
    print("Removed tag '" .. tag .. "' from " .. target.Name)
elseif action == "get" then
    local objects = CS:GetTagged(tag)
    local result = "--- Objects with tag '" .. tag .. "' ---\\n"
    for _, obj in ipairs(objects) do
        result = result .. obj:GetFullName() .. "\\n"
    end
    print(result .. "Total: " .. #objects)
end
"""

RUN_TESTS_LUA = """
-- Simple Test Runner (assuming TestEZ or custom tests)
local function runTests(parent)
    local found = false
    for _, child in ipairs(parent:GetDescendants()) do
        if child:IsA("ModuleScript") and child.Name:find("spec") then
            found = true
            print("Running test: " .. child:GetFullName())
            local status, err = pcall(function() require(child) end)
            if status then
                print("[PASS] " .. child.Name)
            else
                print("[FAIL] " .. child.Name .. ": " .. tostring(err))
            end
        end
    end
    if not found then print("No test specs found.") end
end

print("--- Running Unit Tests ---")
runTests(game.ServerScriptService)
runTests(game.ReplicatedStorage)
"""

GET_STATS_LUA = """
local stats = game:GetService("Stats")
print("--- Studio Performance Stats ---")
print("Memory Usage: " .. string.format("%.2f", stats:GetTotalMemoryUsageMb()) .. " MB")
print("Instance Count: " .. stats.InstanceCount)
print("Draw Calls: " .. stats.PrimitivesRendered)
print("Physics FPS: " .. string.format("%.2f", stats.PhysicsFps))
"""

GET_PROPERTIES_LUA = """
local target = {path}
if not target then print("Error: Object not found.") return end

local function serialize(val)
    if type(val) == "userdata" then
        return tostring(val)
    end
    return val
end

print("--- Properties for: " .. target:GetFullName() .. " ---")
-- Exhaustive property lists for major classes to prevent "blindness"
local classProps = {{
    Lighting = {{"Ambient", "Brightness", "ColorShift_Bottom", "ColorShift_Top", "OutdoorAmbient", "ClockTime", "GeographicLatitude", "EnvironmentDiffuseScale", "EnvironmentSpecularScale", "ExposureCompensation", "FogColor", "FogEnd", "FogStart", "GlobalShadows", "ShadowSoftness"}},
    Atmosphere = {{"Color", "Decay", "Density", "Glare", "Haze", "Offset"}},
    BloomEffect = {{"Intensity", "Size", "Threshold"}},
    ColorCorrectionEffect = {{"Brightness", "Contrast", "Saturation", "TintColor"}},
    SunRaysEffect = {{"Intensity", "Spread"}},
    Sky = {{"SkyboxBk", "SkyboxDn", "SkyboxFt", "SkyboxLf", "SkyboxRt", "SkyboxUp", "SunAngularSize", "MoonAngularSize", "StarCount"}},
    Humanoid = {{"Health", "MaxHealth", "WalkSpeed", "JumpPower", "HipHeight", "MoveDirection", "AutoRotate", "Sit", "PlatformStand", "Jump", "TargetPoint"}},
    BasePart = {{"Anchored", "CanCollide", "CanTouch", "CanQuery", "Mass", "Position", "Size", "CFrame", "Transparency", "Color", "Material", "Reflectance", "Velocity", "RotVelocity", "AssemblyLinearVelocity", "AssemblyAngularVelocity"}},
    Model = {{"PrimaryPart", "WorldPivot"}},
    SpawnLocation = {{"AllowTeamChangeOnTouch", "Duration", "Enabled", "Neutral", "TeamColor"}},
    ParticleEmitter = {{"Color", "Size", "Texture", "Transparency", "ZOffset", "Lifetime", "Rate", "Rotation", "RotSpeed", "Speed", "SpreadAngle", "Enabled"}},
    PointLight = {{"Brightness", "Color", "Range", "Shadows", "Enabled"}},
    SpotLight = {{"Angle", "Brightness", "Color", "Range", "Shadows", "Enabled"}},
    SurfaceLight = {{"Angle", "Brightness", "Color", "Range", "Shadows", "Enabled"}},
    Sound = {{"SoundId", "Volume", "PlaybackSpeed", "Playing", "Looped", "TimePosition"}},
    DataModel = {{"PlaceId", "GameId", "JobId"}},
    Terrain = {{"Decoration", "GrassLength", "WaterColor", "WaterTransparency", "WaterWaveSize", "WaterWaveSpeed"}}
}}

local toCheck = {{"Name", "ClassName", "Parent"}}

-- Add properties based on class and inheritance
for className, props in pairs(classProps) do
    if target:IsA(className) then
        for _, p in ipairs(props) do table.insert(toCheck, p) end
    end
end

-- Deduplicate and sort
local unique = {{}}
local final = {{}}
for _, p in ipairs(toCheck) do
    if not unique[p] then
        unique[p] = true
        table.insert(final, p)
    end
end

for _, prop in ipairs(final) do
    local s, v = pcall(function() return target[prop] end)
    if s then
        print(prop .. ": " .. tostring(serialize(v)))
    end
end
"""

SET_PROPERTY_LUA = """
local target = {path}
local prop = "{property}"
local valRaw = "{value}"

if not target then print("Error: Object not found.") return end

local function convert(v, targetType)
    if targetType == "boolean" then return v == "true" or v == "1"
    elseif targetType == "number" then return tonumber(v)
    elseif targetType == "Vector3" then
        local x,y,z = v:match("([^,]+),([^,]+),([^,]+)")
        return Vector3.new(tonumber(x), tonumber(y), tonumber(z))
    elseif targetType == "Color3" then
        local r,g,b = v:match("([^,]+),([^,]+),([^,]+)")
        if r then return Color3.new(tonumber(r), tonumber(g), tonumber(b)) end
        return Color3.fromHex(v)
    elseif targetType == "BrickColor" then
        local r,g,b = v:match("([^,]+),([^,]+),([^,]+)")
        if r then return BrickColor.new(Color3.new(tonumber(r), tonumber(g), tonumber(b))) end
        return BrickColor.new(v)
    elseif targetType == "CFrame" then
        local parts = {{}}
        for p in v:gmatch("([^,]+)") do table.insert(parts, tonumber(p)) end
        if #parts == 3 then return CFrame.new(parts[1], parts[2], parts[3]) end
        if #parts >= 12 then return CFrame.new(unpack(parts)) end
        return CFrame.new()
    end
    return v
end

local currentVal = target[prop]
local newVal = convert(valRaw, typeof(currentVal))

local s, err = pcall(function() target[prop] = newVal end)
if s then
    print("Successfully set " .. prop .. " to " .. tostring(newVal))
else
    print("Error setting property: " .. tostring(err))
end
"""

FIND_INSTANCES_LUA = """
local root = {root_path}
local className = "{class_name}"
local namePattern = "{name_pattern}"
local results = "--- Find Results ---"
local count = 0

if not root then root = game end

for _, obj in ipairs(root:GetDescendants()) do
    local match = true
    if className ~= "" and obj.ClassName ~= className then match = false end
    if namePattern ~= "" and not obj.Name:find(namePattern) then match = false end
    
    if match then
        results = results .. "\\n" .. obj:GetFullName() .. " [" .. obj.ClassName .. "]"
        count = count + 1
        if count >= 50 then break end
    end
end
print(results .. "\\nTotal found: " .. count)
"""

CREATE_INSTANCE_LUA = """
local parent = {parent_path}
local props = {props_table}
if not parent then print("Error: Parent not found.") return end

local function convert(v, targetType)
    if targetType == "boolean" then return v == true or v == "true" or v == "1"
    elseif targetType == "number" then return tonumber(v)
    elseif targetType == "Vector3" then
        if type(v) == "table" then return Vector3.new(v.x or v[1], v.y or v[2], v.z or v[3]) end
        local x,y,z = tostring(v):match("([^,]+),([^,]+),([^,]+)")
        if x then return Vector3.new(tonumber(x), tonumber(y), tonumber(z)) end
    elseif targetType == "Color3" then
        if type(v) == "table" then return Color3.new(v.r or v[1], v.g or v[2], v.b or v[3]) end
        local r,g,b = tostring(v):match("([^,]+),([^,]+),([^,]+)")
        if r then return Color3.new(tonumber(r), tonumber(g), tonumber(b)) end
        return Color3.fromHex(tostring(v))
    elseif targetType == "BrickColor" then
        if type(v) == "table" then return BrickColor.new(Color3.new(v.r or v[1], v.g or v[2], v.b or v[3])) end
        local r,g,b = tostring(v):match("([^,]+),([^,]+),([^,]+)")
        if r then return BrickColor.new(Color3.new(tonumber(r), tonumber(g), tonumber(b))) end
        return BrickColor.new(tostring(v))
    elseif targetType == "CFrame" then
        if type(v) == "table" then return CFrame.new(unpack(v)) end
        local parts = {{}}
        for p in tostring(v):gmatch("([^,]+)") do table.insert(parts, tonumber(p)) end
        if #parts == 3 then return CFrame.new(parts[1], parts[2], parts[3]) end
        if #parts >= 12 then return CFrame.new(unpack(parts)) end
        return CFrame.new()
    end
    return v
end

local s, obj = pcall(function()
    local newObj = Instance.new("{class_name}")
    newObj.Name = "{name}"
    
    for prop, val in pairs(props) do
        local currentVal = newObj[prop]
        newObj[prop] = convert(val, typeof(currentVal))
    end
    
    newObj.Parent = parent
    
    -- Auto-grounding for Workspace objects
    if parent == workspace or parent:IsDescendantOf(workspace) then
        if newObj:IsA("BasePart") or newObj:IsA("Model") then
            local currentPos = newObj:IsA("Model") and newObj:GetPivot().Position or newObj.Position
            -- Only ground if Y is default/low or explicitly requested
            if currentPos.Y < 10 then
                local groundedPos = _G.Helper.getGround(currentPos)
                if newObj:IsA("Model") then
                    newObj:PivotTo(CFrame.new(groundedPos + Vector3.new(0, 2, 0)))
                else
                    newObj.Position = groundedPos + Vector3.new(0, newObj.Size.Y/2, 0)
                end
            end
        end
    end
    
    return newObj
end)

if s then
    print("Created " .. obj.ClassName .. " '" .. obj.Name .. "' at " .. obj:GetFullName())
else
    print("Error creating instance: " .. tostring(obj))
end
"""

DELETE_INSTANCE_LUA = """
local target = {path}
if not target then print("Error: Object not found.") return end

local name = target.Name
local fullName = target:GetFullName()
local s, err = pcall(function() target:Destroy() end)

if s then
    print("Successfully deleted: " .. fullName)
else
    print("Error deleting " .. name .. ": " .. tostring(err))
end
"""

RAYCAST_LUA = """
local originStr = "{origin}"
local dirStr = "{direction}"

local function toVec3(s)
    local x,y,z = s:match("([^,]+),([^,]+),([^,]+)")
    return Vector3.new(tonumber(x), tonumber(y), tonumber(z))
end

local origin = toVec3(originStr)
local dir = toVec3(dirStr)

local result = workspace:Raycast(origin, dir)
if result then
    print("Raycast Hit!")
    print("Instance: " .. result.Instance:GetFullName())
    print("Position: " .. tostring(result.Position))
    print("Distance: " .. result.Distance)
    print("Material: " .. result.Material.Name)
else
    print("Raycast missed.")
end
"""

INSERT_ASSET_LUA = """
local InsertService = game:GetService("InsertService")
local assetId = {asset_id}
local posStr = "{position}"

local function toVec3(s)
    local x,y,z = s:match("([^,]+),([^,]+),([^,]+)")
    return Vector3.new(tonumber(x), tonumber(y), tonumber(z))
end

local success, model = pcall(function()
    return InsertService:LoadAsset(assetId)
end)

if success and model then
    model.Parent = workspace
    model:MoveTo(toVec3(posStr))
    model:MakeJoints()
    print("Successfully inserted and placed asset " .. assetId .. " at " .. posStr)
else
    print("Error inserting asset: " .. tostring(model))
end
"""

PUBLISH_GAME_LUA = """
local StudioService = game:GetService("StudioService")
if game.PlaceId == 0 then
    print("Error: This place is not published yet. Please File > Publish once manually.")
else
    local success, err = pcall(function()
        StudioService:PublishToRoblox()
    end)
    if success then
        print("Successfully Published! Place ID: " .. game.PlaceId)
    else
        print("Publish failed: " .. tostring(err))
    end
end
"""

MODIFY_INSTANCE_LUA = """
local target = {path}
local props = {props_table}

if not target then print("Error: Object not found.") return end

local function convert(v, targetType)
    if targetType == "boolean" then return v == true or v == "true" or v == "1"
    elseif targetType == "number" then return tonumber(v)
    elseif targetType == "Vector3" then
        if type(v) == "table" then return Vector3.new(v.x or v[1], v.y or v[2], v.z or v[3]) end
        local x,y,z = tostring(v):match("([^,]+),([^,]+),([^,]+)")
        if x then return Vector3.new(tonumber(x), tonumber(y), tonumber(z)) end
    elseif targetType == "Color3" then
        if type(v) == "table" then return Color3.new(v.r or v[1], v.g or v[2], v.b or v[3]) end
        local r,g,b = tostring(v):match("([^,]+),([^,]+),([^,]+)")
        if r then return Color3.new(tonumber(r), tonumber(g), tonumber(b)) end
        return Color3.fromHex(tostring(v))
    elseif targetType == "BrickColor" then
        if type(v) == "table" then return BrickColor.new(Color3.new(v.r or v[1], v.g or v[2], v.b or v[3])) end
        local r,g,b = tostring(v):match("([^,]+),([^,]+),([^,]+)")
        if r then return BrickColor.new(Color3.new(tonumber(r), tonumber(g), tonumber(b))) end
        return BrickColor.new(tostring(v))
    elseif targetType == "CFrame" then
        if type(v) == "table" then return CFrame.new(unpack(v)) end
        local parts = {{}}
        for p in tostring(v):gmatch("([^,]+)") do table.insert(parts, tonumber(p)) end
        if #parts == 3 then return CFrame.new(parts[1], parts[2], parts[3]) end
        if #parts >= 12 then return CFrame.new(unpack(parts)) end
        return CFrame.new()
    end
    return v
end

print("--- Modifying Instance: " .. target:GetFullName() .. " ---")
for prop, val in pairs(props) do
    local s, err = pcall(function() 
    local currentVal = target[prop]
        target[prop] = convert(val, typeof(currentVal)) 
    end)
    if s then
        print("Set " .. prop .. " successfully.")
    else
        print("Error setting " .. prop .. ": " .. tostring(err))
    end
end
"""

GET_STUDIO_STATE_LUA = """
local RunService = game:GetService("RunService")
local state = "UNKNOWN"

if RunService:IsRunning() then
    if RunService:IsClient() then state = "PLAY_MODE (CLIENT)"
    elseif RunService:IsServer() then state = "PLAY_MODE (SERVER)"
    else state = "PLAY_MODE" end
else
    state = "EDIT_MODE"
end

print("--- Studio State ---")
print("Mode: " .. state)
print("PlaceId: " .. game.PlaceId)
print("UniverseId: " .. game.GameId)
if state == "EDIT_MODE" then
    print("TIP: Some objects (like zombies from spawners) only exist in PLAY_MODE.")
end
"""

MANIPULATE_TERRAIN_LUA = """
local terrain = workspace.Terrain
local action = "{action}"
local mat_str = "{material}"
local pos_str = "{position}"
local size_str = "{size}"

local material_map = {{
    Dirt = Enum.Material.Ground,
    Stone = Enum.Material.Rock,
    Water = Enum.Material.Water,
    Lava = Enum.Material.CrackedLava,
    Sand = Enum.Material.Sand,
    Snow = Enum.Material.Snow,
    Grass = Enum.Material.Grass,
    Air = Enum.Material.Air
}}

local material = material_map[mat_str] or Enum.Material[mat_str] or Enum.Material.Grass

local function toVec3(s)
    local x,y,z = s:match("([^,]+),([^,]+),([^,]+)")
    if not x then return Vector3.new(0,0,0) end
    return Vector3.new(tonumber(x), tonumber(y), tonumber(z))
end

local function toCFrame(s)
    local parts = {{}}
    for p in s:gmatch("([^,]+)") do table.insert(parts, tonumber(p)) end
    if #parts == 3 then return CFrame.new(parts[1], parts[2], parts[3]) end
    if #parts >= 12 then return CFrame.new(unpack(parts)) end
    return CFrame.new()
end

print("--- Manipulating Terrain (" .. tostring(material) .. ") ---")
local success, err = pcall(function()
    if action == "fillBlock" then
        terrain:FillBlock(toCFrame(pos_str), toVec3(size_str), material)
    elseif action == "fillBall" then
        terrain:FillBall(toVec3(pos_str), tonumber(size_str), material)
    elseif action == "fillCylinder" then
        local r, h = size_str:match("([^,]+),([^,]+)")
        terrain:FillCylinder(toCFrame(pos_str), tonumber(h), tonumber(r), material)
    end
end)

if success then
    print("Terrain " .. action .. " completed.")
else
    print("Terrain error: " .. tostring(err))
end
"""

GENERATE_TERRAIN_LUA = """
local terrain = workspace.Terrain
local pos = Vector3.new({x}, {y}, {z})
local size = Vector2.new({width}, {depth})
local scale = {scale}
local amp = {amplitude}
local mat = Enum.Material.{material}
local biome = "{biome}"

print("--- Generating Procedural Terrain (" .. biome .. ") ---")

for x = -size.X/2, size.X/2, 4 do
    for z = -size.Y/2, size.Y/2, 4 do
        local noise = math.noise(x/scale, z/scale, 0)
        
        -- Apply biome modifiers
        if biome == "mountains" then 
            noise = math.abs(noise) * 2
        elseif biome == "craters" then 
            noise = -math.abs(noise)
        elseif biome == "plains" then
            noise = noise * 0.2
        end
        
        local height = noise * amp
        local fillPos = pos + Vector3.new(x, height/2, z)
        local fillSize = Vector3.new(4, math.max(1, height + 20), 4)
        
        terrain:FillBlock(CFrame.new(fillPos), fillSize, mat)
    end
end

-- Spawn Recovery: Snap SpawnLocation to surface
local spawn = workspace:FindFirstChildWhichIsA("SpawnLocation", true)
if spawn then
    local ray = workspace:Raycast(spawn.Position + Vector3.new(0, 100, 0), Vector3.new(0, -200, 0))
    if ray then
        spawn.Position = ray.Position + Vector3.new(0, spawn.Size.Y/2, 0)
    else
        -- Fallback to center ground if spawn is way off
        spawn.Position = _G.Helper.getGround(Vector3.new(0,0,0)) + Vector3.new(0, spawn.Size.Y/2, 0)
    end
end

print("Generation complete.")
"""

SMART_SETUP_LUA = """
local InsertService = game:GetService("InsertService")
local MarketplaceService = game:GetService("MarketplaceService")
local query = "{query}"
local posStr = "{position}"

local function toVec3(s)
    local x,y,z = s:match("([^,]+),([^,]+),([^,]+)")
    if not x then return Vector3.new(0,5,0) end
    return Vector3.new(tonumber(x), tonumber(y), tonumber(z))
end

print("--- Smart Asset Setup: " .. query .. " ---")

local success, result = pcall(function()
    local search = InsertService:GetFreeModels(query, 0)
    if not search then error("Marketplace search returned nil for query: " .. query) end
    
    local pages = search:GetCurrentPage()
    if #pages == 0 then error("No results found for query: " .. query) end
    
    local assetId = pages[1].AssetId
    local model = InsertService:LoadAsset(assetId)
    model.Parent = workspace
    
    local targetPos = toVec3(posStr)
    -- Auto-grounding: search for surface
    local groundedPos = _G.Helper.getGround(targetPos)
    model:MoveTo(groundedPos)
    model:MakeJoints()
    
    local payload = nil
    local category = "Unknown"
    
    -- Scan for Tools
    for _, item in ipairs(model:GetDescendants()) do
        if item:IsA("Tool") then
            item.Parent = game:GetService("StarterPack")
            payload = item
            category = "Weapon/Tool"
            break
        end
    end
    
    -- Scan for NPCs
    if not payload then
        for _, item in ipairs(model:GetDescendants()) do
            if item:IsA("Humanoid") then
                local npc = item.Parent
                npc.Parent = game:GetService("ServerStorage")
                payload = npc
                category = "NPC"
                break
            end
        end
    end
    
    local finalPath = payload and payload:GetFullName() or model:GetFullName()
    print("Successfully setup " .. category .. " at " .. finalPath)
    
    -- Cleanup empty wrapper if payload was moved
    if payload and payload.Parent ~= model then
        model:Destroy()
    end
    
    return finalPath
end)

if not success then
    print("Error in smart setup: " .. tostring(result))
end
"""

SCATTER_LUA = """
local path = {path}
local count = {count}
local radius = {radius}

if not path then 
    print("Error: Source object for scattering not found. Please verify the path.") 
    return 
end

print("--- Scattering " .. count .. " instances of " .. path.Name .. " ---")
local success, err = pcall(function()
    -- Ensure Helper exists
    if not _G.Helper then error("LUA_UTILS / _G.Helper not initialized correctly.") end
    _G.Helper.scatter(path, count, radius, workspace)
end)

if success then
    print("Scattering complete.")
else
    print("Error during scattering: " .. tostring(err))
end
"""

MARKETPLACE_INFO_LUA = """
local assetId = {asset_id}
local MarketplaceService = game:GetService("MarketplaceService")
local InsertService = game:GetService("InsertService")

local success, result = pcall(function()
    local info = MarketplaceService:GetProductInfo(assetId)
    
    -- Content Scan: Insert to nil, count classes, then destroy
    local classCounts = {{}}
    local totalParts = 0
    local model = InsertService:LoadAsset(assetId)
    
    for _, item in ipairs(model:GetDescendants()) do
        local cls = item.ClassName
        classCounts[cls] = (classCounts[cls] or 0) + 1
        if item:IsA("BasePart") then totalParts = totalParts + 1 end
    end
    model:Destroy()
    
    return {{info = info, counts = classCounts, parts = totalParts}}
end)

if success then
    local data = result
    print("--- Marketplace Info for " .. assetId .. " ---")
    print("Name: " .. data.info.Name)
    print("Creator: " .. data.info.Creator.Name)
    print("Description: " .. data.info.Description)
    
    local countStr = ""
    for cls, count in pairs(data.counts) do
        countStr = countStr .. cls .. ": " .. count .. ", "
    end
    print("Contents: " .. (countStr ~= "" and countStr:sub(1, -3) or "None"))
else
    print("Error fetching info: " .. tostring(result))
end
"""

CREATE_SPAWNER_LUA = """
local template = {template_path}
local containerName = "{container_name}"
local interval = {interval}
local maxCount = {max_count}
local centerStr = "{spawn_area_center}"
local radius = {spawn_radius}

if not template then 
    print("Error: Template for spawner not found at path.") 
    return 
end

local function toVec3(s)
    local x,y,z = s:match("([^,]+),([^,]+),([^,]+)")
    return Vector3.new(tonumber(x), tonumber(y), tonumber(z))
end

local center = toVec3(centerStr)

local success, err = pcall(function()
    local folder = workspace:FindFirstChild(containerName)
    if not folder then
        folder = Instance.new("Folder")
        folder.Name = containerName
        folder.Parent = workspace
    end
    
    local spawnerScript = Instance.new("Script")
    spawnerScript.Name = containerName .. "_Spawner"
    spawnerScript.Source = string.format([[
        local template = %s
        local folder = workspace:WaitForChild("%s")
        local interval = %f
        local maxCount = %d
        local center = Vector3.new(%f, %f, %f)
        local radius = %f
        
        while true do
            task.wait(interval)
            if #folder:GetChildren() < maxCount then
                local clone = template:Clone()
                local x = center.X + (math.random() - 0.5) * radius * 2
                local z = center.Z + (math.random() - 0.5) * radius * 2
                clone.Parent = folder
                if clone:IsA("Model") then
                    clone:MoveTo(Vector3.new(x, center.Y + 50, z))
                else
                    clone.Position = Vector3.new(x, center.Y + 50, z)
                end
                
                -- Simple ground detection
                local ray = workspace:Raycast(Vector3.new(x, center.Y + 100, z), Vector3.new(0, -200, 0))
                if ray then
                    if clone:IsA("Model") then clone:MoveTo(ray.Position) else clone.Position = ray.Position end
                end
            end
        end
    ]], template:GetFullName(), containerName, interval, maxCount, center.X, center.Y, center.Z, radius)
    
    spawnerScript.Parent = workspace
end)

if success then
    print("Successfully created spawner: " .. containerName .. "_Spawner")
else
    print("Error creating spawner: " .. tostring(err))
end
"""
