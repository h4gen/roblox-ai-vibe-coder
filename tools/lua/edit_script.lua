local target = {script_path}
if target and (target:IsA("LuaSourceContainer")) then
    -- Basic Syntax Check
    local newSource = [===[{new_source}]===]
    local func, err = loadstring(newSource)
    if not func then
        print("Error: Syntax error in new source code. Change NOT applied.\n" .. err)
    else
        target.Source = newSource
        print("Successfully updated script: " .. target.Name)
    end
else
    print("Error: Could not find script at path '{script_path}' to edit.")
end

