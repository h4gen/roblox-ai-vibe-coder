local root = {root_path}
local className = "{class_name}"
local namePattern = "{name_pattern}"
local results = "--- Find Results ---"
local count = 0

if not root then root = game end

for _, obj in ipairs(root:GetDescendants()) do
    local match = true
    if className ~= "" and obj.ClassName ~= className then match = false end
    if namePattern ~= "" and not obj.Name:find(namePattern) then match = false end
    
    if match then
        results = results .. "\n" .. obj:GetFullName() .. " [" .. obj.ClassName .. "]"
        count = count + 1
        if count >= 50 then break end
    end
end
return results .. "\nTotal found: " .. count

