local function toVec3(s)
    if type(s) == "table" then return Vector3.new(s.x or s[1], s.y or s[2], s.z or s[3]) end
    local x,y,z = tostring(s):match("([^,]+),([^,]+),([^,]+)")
    return Vector3.new(tonumber(x), tonumber(y), tonumber(z))
end

local origin = toVec3(args.origin)
local dir = toVec3(args.direction)

local result = workspace:Raycast(origin, dir)
if result then
    local res = "Raycast Hit!\n"
    res = res .. "Instance: " .. result.Instance:GetFullName() .. "\n"
    res = res .. "Position: " .. tostring(result.Position) .. "\n"
    res = res .. "Distance: " .. result.Distance .. "\n"
    res = res .. "Material: " .. result.Material.Name .. "\n"
    return res
else
    return "Raycast missed."
end
