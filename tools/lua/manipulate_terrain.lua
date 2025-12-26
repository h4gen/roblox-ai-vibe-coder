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

