local target, targetErr = SafeResolve(args.path)
local newParent, parentErr = SafeResolve(args.new_parent)

if not target then return "Error: Target object not found. " .. (targetErr or "") end
if not newParent then return "Error: New parent not found. " .. (parentErr or "") end

local success, err = pcall(function()
    target.Parent = newParent
end)

if success then
    return "Successfully moved " .. target.Name .. " to " .. newParent:GetFullName()
else
    return "Error moving object: " .. tostring(err)
end
