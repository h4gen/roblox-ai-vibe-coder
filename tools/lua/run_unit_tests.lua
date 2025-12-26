local function runTests(parent)
    local found = false
    local res = ""
    for _, child in ipairs(parent:GetDescendants()) do
        if child:IsA("ModuleScript") and child.Name:find("spec") then
            found = true
            res = res .. "Running test: " .. child:GetFullName() .. "\n"
            local status, err = pcall(function() require(child) end)
            if status then
                res = res .. "[PASS] " .. child.Name .. "\n"
            else
                res = res .. "[FAIL] " .. child.Name .. ": " .. tostring(err) .. "\n"
            end
        end
    end
    return found, res
end

local output = "--- Running Unit Tests ---\n"
local f1, r1 = runTests(game.ServerScriptService)
local f2, r2 = runTests(game.ReplicatedStorage)
output = output .. r1 .. r2
if not f1 and not f2 then output = output .. "No test specs found.\n" end
return output
