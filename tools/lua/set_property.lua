local target, err = SafeResolve(args.path)
local prop = args.property
local valRaw = args.value

if not target then return "Error: Object not found. " .. (err or "") end

local function convert(v, targetType)
    if targetType == "boolean" then return v == true or v == "true" or v == "1"
    elseif targetType == "number" then return tonumber(v)
    elseif targetType == "string" then return tostring(v)
    elseif targetType == "Vector3" then
        if type(v) == "table" then return Vector3.new(v.x or v[1], v.y or v[2], v.z or v[3]) end
        local x,y,z = tostring(v):match("([^,]+),([^,]+),([^,]+)")
        if x then return Vector3.new(tonumber(x), tonumber(y), tonumber(z)) end
    elseif targetType == "Color3" then
        if type(v) == "table" then 
            return Color3.fromRGB(v.r or v[1], v.g or v[2], v.b or v[3])
        end
        local s = tostring(v)
        local r,g,b = s:match("([^,]+),([^,]+),([^,]+)")
        if r then return Color3.fromRGB(tonumber(r), tonumber(g), tonumber(b)) end
        if s:sub(1,1) == "#" then return Color3.fromHex(s) end
        
        -- Smart Color Names
        local names = {Red=Color3.new(1,0,0), Green=Color3.new(0,1,0), Blue=Color3.new(0,0,1), White=Color3.new(1,1,1), Black=Color3.new(0,0,0), Yellow=Color3.new(1,1,0), Cyan=Color3.new(0,1,1), Magenta=Color3.new(1,0,1), Grey=Color3.new(0.5,0.5,0.5)}
        if names[s] then return names[s] end
        
        return Color3.fromHex(s) -- Try hex as fallback
        
    elseif targetType == "BrickColor" then
        if type(v) == "table" then return BrickColor.new(Color3.new(v.r or v[1], v.g or v[2], v.b or v[3])) end
        return BrickColor.new(tostring(v))
        
    elseif targetType == "UDim2" then
        if type(v) == "table" then return UDim2.new(v[1], v[2], v[3], v[4]) end
        local s = tostring(v):gsub("[{}]", "") -- Remove braces
        local parts = {}
        for p in s:gmatch("([^,]+)") do table.insert(parts, tonumber(p)) end
        if #parts == 4 then return UDim2.new(parts[1], parts[2], parts[3], parts[4]) end
        return UDim2.new(0,0,0,0)
        
    elseif typeof(targetType) == "EnumItem" then
        -- Smart Enum matching
        local enumName = tostring(targetType.EnumType)
        local success, val = pcall(function() return Enum[enumName][v] end)
        if success then return val end
        return v
        
    elseif targetType == "CFrame" then
        if type(v) == "table" then return CFrame.new(unpack(v)) end
        local parts = {}
        for p in tostring(v):gmatch("([^,]+)") do table.insert(parts, tonumber(p)) end
        if #parts == 3 then return CFrame.new(parts[1], parts[2], parts[3]) end
        if #parts >= 12 then return CFrame.new(unpack(parts)) end
        return CFrame.new()
    end
    return v
end

local currentVal = target[prop]
local newVal = convert(valRaw, typeof(currentVal))

local s, setErr = pcall(function() target[prop] = newVal end)
if s then
    return "Successfully set " .. prop .. " to " .. tostring(newVal)
else
    return "Error setting property: " .. tostring(setErr)
end
