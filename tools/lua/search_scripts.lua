local pattern = args.pattern
local results = "--- Search Results for '" .. tostring(pattern) .. "' ---\n"
local count = 0

local function search(obj)
    if obj:IsA("LuaSourceContainer") then
        if obj.Source:find(pattern) then
            results = results .. obj:GetFullName() .. "\n"
            count = count + 1
        end
    end
    for _, child in ipairs(obj:GetChildren()) do
        search(child)
    end
end

search(game)
return results .. "Total found: " .. count
