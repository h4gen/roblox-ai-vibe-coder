local terrain = workspace.Terrain
local pos = Vector3.new({x}, {y}, {z})
local size = Vector2.new({width}, {depth})
local scale = {scale}
local amp = {amplitude}
local mat = Enum.Material.{material}
local biome = "{biome}"

local function getGround(pos)
    local params = RaycastParams.new()
    params.FilterDescendantsInstances = {workspace:FindFirstChild("Baseplate")}
    params.FilterType = Enum.RaycastFilterType.Include
    local ray = workspace:Raycast(pos + Vector3.new(0, 50, 0), Vector3.new(0, -100, 0), params)
    if not ray then
        ray = workspace:Raycast(pos + Vector3.new(0, 50, 0), Vector3.new(0, -100, 0))
    end
    return ray and ray.Position or pos
end

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
        spawn.Position = getGround(Vector3.new(0,0,0)) + Vector3.new(0, spawn.Size.Y/2, 0)
    end
end

print("Generation complete.")

