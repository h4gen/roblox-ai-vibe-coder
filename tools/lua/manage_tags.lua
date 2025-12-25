local CS = game:GetService("CollectionService")
local target = {path}
local action = "{action}"
local tag = "{tag}"

if not target then print("Error: Object not found.") return end

if action == "add" then
    CS:AddTag(target, tag)
    print("Added tag '" .. tag .. "' to " .. target.Name)
elseif action == "remove" then
    CS:RemoveTag(target, tag)
    print("Removed tag '" .. tag .. "' from " .. target.Name)
elseif action == "get" then
    local objects = CS:GetTagged(tag)
    local result = "--- Objects with tag '" .. tag .. "' ---\n"
    for _, obj in ipairs(objects) do
        result = result .. obj:GetFullName() .. "\n"
    end
    print(result .. "Total: " .. #objects)
end

