local parent, parentErr = SafeResolve(args.parent_path)
local props = args.properties or {}
local children = args.children or {}

if not parent then return "Error: Parent not found. " .. (parentErr or "") end

local function getGround(pos)
    local params = RaycastParams.new()
    params.FilterDescendantsInstances = {workspace:FindFirstChild("Baseplate")}
    params.FilterType = Enum.RaycastFilterType.Include
    local ray = workspace:Raycast(pos + Vector3.new(0, 50, 0), Vector3.new(0, -100, 0), params)
    if not ray then
        local tParams = RaycastParams.new()
        tParams.FilterDescendantsInstances = {workspace.Terrain}
        tParams.FilterType = Enum.RaycastFilterType.Include
        ray = workspace:Raycast(pos + Vector3.new(0, 50, 0), Vector3.new(0, -100, 0), tParams)
    end
    if not ray then
        ray = workspace:Raycast(pos + Vector3.new(0, 50, 0), Vector3.new(0, -100, 0))
    end
    return ray and ray.Position or pos
end

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
        local names = {Red=Color3.new(1,0,0), Green=Color3.new(0,1,0), Blue=Color3.new(0,0,1), White=Color3.new(1,1,1), Black=Color3.new(0,0,0), Yellow=Color3.new(1,1,0), Cyan=Color3.new(0,1,1), Magenta=Color3.new(1,0,1), Grey=Color3.new(0.5,0.5,0.5)}
        if names[s] then return names[s] end
        return Color3.fromHex(s)
    elseif targetType == "BrickColor" then
        if type(v) == "table" then return BrickColor.new(Color3.new(v.r or v[1], v.g or v[2], v.b or v[3])) end
        return BrickColor.new(tostring(v))
    elseif targetType == "UDim2" then
        if type(v) == "table" then return UDim2.new(v[1], v[2], v[3], v[4]) end
        local s = tostring(v):gsub("[{}]", "")
        local parts = {}
        for p in s:gmatch("([^,]+)") do table.insert(parts, tonumber(p)) end
        if #parts == 4 then return UDim2.new(parts[1], parts[2], parts[3], parts[4]) end
        return UDim2.new(0,0,0,0)
    elseif typeof(targetType) == "EnumItem" then
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

local function createRecursive(def, p)
    local cls = def.class_name
    local name = def.name or cls
    local properties = def.properties or {}
    local kids = def.children or {}
    
    local newObj = Instance.new(cls)
    newObj.Name = name
    
    for prop, val in pairs(properties) do
        local success, err = pcall(function()
            local currentVal = newObj[prop]
            newObj[prop] = convert(val, typeof(currentVal))
        end)
    end
    
    if (p == workspace or p:IsDescendantOf(workspace)) and (newObj:IsA("BasePart") or newObj:IsA("Model")) then
        local currentPos = newObj:IsA("Model") and newObj:GetPivot().Position or newObj.Position
        if currentPos.Y < 10 then
             local groundedPos = getGround(currentPos)
             if newObj:IsA("Model") then
                 newObj:PivotTo(CFrame.new(groundedPos + Vector3.new(0, newObj:GetExtentsSize().Y/2, 0)))
             else
                 newObj.Position = groundedPos + Vector3.new(0, newObj.Size.Y/2, 0)
             end
        end
    end
    
    newObj.Parent = p
    for _, childDef in ipairs(kids) do createRecursive(childDef, newObj) end
    return newObj
end

local s, obj = pcall(function()
    return createRecursive({class_name=args.class_name, name=args.name, properties=props, children=children}, parent)
end)

if s then
    return "Created " .. obj.ClassName .. " '" .. obj.Name .. "' at " .. obj:GetFullName()
else
    return "Error creating instance: " .. tostring(obj)
end
