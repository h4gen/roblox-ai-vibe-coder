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

    local result = obj.Name .. meta .. "\n"
    for _, child in ipairs(obj:GetChildren()) do
        result = result .. string.rep("  ", depth + 1) .. getHierarchy(child, depth + 1, maxDepth)
    end
    return result
end

local service_name = args.service_name or "Workspace"
local max_depth = args.depth or 4

local success, s = pcall(function() return game:GetService(service_name) end)
if success and s then 
    return getHierarchy(s, 0, max_depth) 
else 
    return "Error: Service '" .. tostring(service_name) .. "' not found." 
end
