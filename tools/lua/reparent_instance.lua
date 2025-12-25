local target = {path}
local newParent = {new_parent}

if not target then print("Error: Target object not found at path.") return end
if not newParent then print("Error: New parent not found at path.") return end

local success, err = pcall(function()
    target.Parent = newParent
end)

if success then
    print("Successfully moved " .. target.Name .. " to " .. newParent.Name)
else
    print("Error moving object: " .. tostring(err))
end

