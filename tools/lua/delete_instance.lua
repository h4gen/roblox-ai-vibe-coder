local target, err = SafeResolve(args.path)
if not target then return "Error: Object not found. " .. (err or "") end

local fullName = target:GetFullName()
local s, destroyErr = pcall(function() target:Destroy() end)

if s then
    return "Successfully deleted: " .. fullName
else
    return "Error deleting " .. fullName .. ": " .. tostring(destroyErr)
end
