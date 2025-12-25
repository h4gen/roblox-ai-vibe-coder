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

