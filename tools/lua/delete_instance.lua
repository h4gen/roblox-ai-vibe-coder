local target = {path}
if not target then print("Error: Object not found.") return end

local name = target.Name
local fullName = target:GetFullName()
local s, err = pcall(function() target:Destroy() end)

if s then
    print("Successfully deleted: " .. fullName)
else
    print("Error deleting " .. name .. ": " .. tostring(err))
end

