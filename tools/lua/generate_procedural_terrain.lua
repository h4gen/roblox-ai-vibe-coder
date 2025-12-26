local terrain = workspace.Terrain

local function toVec3(s)
    if type(s) == "table" then return Vector3.new(s.x or s[1], s.y or s[2], s.z or s[3]) end
    local x,y,z = tostring(s):match("([^,]+),([^,]+),([^,]+)")
    return Vector3.new(tonumber(x or 0), tonumber(y or 0), tonumber(z or 0))
end

local function toVec2(s)
    if type(s) == "table" then return Vector2.new(s.x or s[1], s.y or s[2]) end
    local x,y = tostring(s):match("([^,]+),([^,]+)")
    return Vector2.new(tonumber(x or 100), tonumber(y or 100))
end

local pos = toVec3(args.position)
local size = toVec2(args.size)
local scale = args.scale or 100
local amp = args.amplitude or 50
local mat = Enum.Material[args.material or "Grass"] or Enum.Material.Grass
local biome = args.biome or "hills"

local function getGround(p)
    local params = RaycastParams.new()
    params.FilterDescendantsInstances = {workspace:FindFirstChild("Baseplate")}
    params.FilterType = Enum.RaycastFilterType.Include
    local ray = workspace:Raycast(p + Vector3.new(0, 50, 0), Vector3.new(0, -100, 0), params)
    if not ray then
        ray = workspace:Raycast(p + Vector3.new(0, 50, 0), Vector3.new(0, -100, 0))
    end
    return ray and ray.Position or p
end

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

task.wait(1)

local spawn = workspace:FindFirstChildWhichIsA("SpawnLocation", true)
if spawn then
    local params = RaycastParams.new()
    params.FilterType = Enum.RaycastFilterType.Exclude
    params.FilterDescendantsInstances = {spawn}
    
    local ray = workspace:Raycast(spawn.Position + Vector3.new(0, 500, 0), Vector3.new(0, -1000, 0), params)
    if ray then
        spawn.Position = ray.Position + Vector3.new(0, spawn.Size.Y/2, 0)
    else
        spawn.Position = getGround(Vector3.new(0,0,0)) + Vector3.new(0, spawn.Size.Y/2, 0)
    end
end

return "Procedural terrain generation complete (" .. biome .. ")"
