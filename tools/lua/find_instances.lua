local root, err = SafeResolve(args.root_path or "game")
local className = args.class_name or ""
local namePattern = args.name_pattern or ""
local res = "--- Find Results ---"
local count = 0
local classCounts = {}
local foundPaths = {}

if not root then root = game end

for _, obj in ipairs(root:GetDescendants()) do
    local match = true
    if className ~= "" and obj.ClassName ~= className then match = false end
    if namePattern ~= "" and not obj.Name:find(namePattern) then match = false end
    
    if match then
        count = count + 1
        classCounts[obj.ClassName] = (classCounts[obj.ClassName] or 0) + 1
        if #foundPaths < 50 then
            table.insert(foundPaths, obj:GetFullName() .. " [" .. obj.ClassName .. "]")
        end
    end
end

res = res .. "\n" .. table.concat(foundPaths, "\n")

if count > 50 then
    res = res .. "\n\n[WARNING: Search Saturated]"
    res = res .. "\nFound " .. count .. " total matches. Listing top 50 above."
    res = res .. "\nClass breakdown of all matches:"
    for cls, c in pairs(classCounts) do
        res = res .. "\n- " .. cls .. ": " .. c
    end
    res = res .. "\nTIP: Use a more specific 'class_name' or a smaller 'root_path' to narrow results."
else
    res = res .. "\nTotal found: " .. count
end

return res
