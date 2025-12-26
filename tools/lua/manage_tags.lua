local CS = game:GetService("CollectionService")
local action = args.action
local tag = args.tag

if action == "add" then
    local target, err = SafeResolve(args.path)
    if not target then return "Error: Object not found. " .. (err or "") end
    CS:AddTag(target, tag)
    return "Added tag '" .. tag .. "' to " .. target.Name
elseif action == "remove" then
    local target, err = SafeResolve(args.path)
    if not target then return "Error: Object not found. " .. (err or "") end
    CS:RemoveTag(target, tag)
    return "Removed tag '" .. tag .. "' from " .. target.Name
elseif action == "get" then
    local objects = CS:GetTagged(tag)
    local result = "--- Objects with tag '" .. tag .. "' ---\n"
    for _, obj in ipairs(objects) do
        result = result .. obj:GetFullName() .. "\n"
    end
    return result .. "Total: " .. #objects
end
return "Error: Unknown action '" .. tostring(action) .. "'"
