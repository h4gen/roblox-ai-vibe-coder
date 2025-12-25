-- Simple Test Runner (assuming TestEZ or custom tests)
local function runTests(parent)
    local found = false
    for _, child in ipairs(parent:GetDescendants()) do
        if child:IsA("ModuleScript") and child.Name:find("spec") then
            found = true
            print("Running test: " .. child:GetFullName())
            local status, err = pcall(function() require(child) end)
            if status then
                print("[PASS] " .. child.Name)
            else
                print("[FAIL] " .. child.Name .. ": " .. tostring(err))
            end
        end
    end
    if not found then print("No test specs found.") end
end

print("--- Running Unit Tests ---")
runTests(game.ServerScriptService)
runTests(game.ReplicatedStorage)

