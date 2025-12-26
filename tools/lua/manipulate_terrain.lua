local terrain = workspace.Terrain
local action = args.action
local mat_str = args.material or "Grass"
local pos_str = args.position
local size_str = args.size

local material_map = {
    Dirt = Enum.Material.Ground,
    Stone = Enum.Material.Rock,
    Water = Enum.Material.Water,
    Lava = Enum.Material.CrackedLava,
    Sand = Enum.Material.Sand,
    Snow = Enum.Material.Snow,
    Grass = Enum.Material.Grass,
    Air = Enum.Material.Air
}

local material = material_map[mat_str] or Enum.Material[mat_str] or Enum.Material.Grass

local function toVec3(s)
    if type(s) == "table" then return Vector3.new(s.x or s[1], s.y or s[2], s.z or s[3]) end
    local x,y,z = tostring(s):match("([^,]+),([^,]+),([^,]+)")
    if not x then return Vector3.new(0,0,0) end
    return Vector3.new(tonumber(x), tonumber(y), tonumber(z))
end

local function toCFrame(s)
    if type(s) == "table" then 
        if #s >= 12 then return CFrame.new(unpack(s)) end
        return CFrame.new(s.x or s[1], s.y or s[2], s.z or s[3]) 
    end
    local parts = {}
    for p in tostring(s):gmatch("([^,]+)") do table.insert(parts, tonumber(p)) end
    if #parts == 3 then return CFrame.new(parts[1], parts[2], parts[3]) end
    if #parts >= 12 then return CFrame.new(unpack(parts)) end
    return CFrame.new()
end

local success, err = pcall(function()
    if action == "fillBlock" then
        terrain:FillBlock(toCFrame(pos_str), toVec3(size_str), material)
    elseif action == "fillBall" then
        terrain:FillBall(toVec3(pos_str), tonumber(size_str), material)
    elseif action == "fillCylinder" then
        local r, h
        if type(size_str) == "string" then
            r, h = size_str:match("([^,]+),([^,]+)")
        elseif type(size_str) == "table" then
            r, h = size_str[1], size_str[2]
        end
        terrain:FillCylinder(toCFrame(pos_str), tonumber(h), tonumber(r), material)
    end
end)

if success then
    return "Terrain " .. tostring(action) .. " completed."
else
    return "Terrain error: " .. tostring(err)
end
