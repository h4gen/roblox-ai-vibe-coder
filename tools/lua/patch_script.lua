local target = {script_path}
if target and (target:IsA("LuaSourceContainer")) then
    local oldSource = target.Source
    local search = [===[{search_string}]===]
    local replace = [===[{replace_string}]===]
    
    -- Use string.find with 'true' for literal search (no patterns)
    local startIdx, endIdx = string.find(oldSource, search, 1, true)
    if startIdx then
        local newSource = string.sub(oldSource, 1, startIdx - 1) .. replace .. string.sub(oldSource, endIdx + 1)
        -- Syntax Check
        local func, err = loadstring(newSource)
        if not func then
             print("Error: Syntax error in patched source code. Change NOT applied.\n" .. err)
        else
            target.Source = newSource
            print("Successfully patched script: " .. target.Name)
        end
    else
        print("Error: Search string not found in script (literal match failed).")
    end
else
    print("Error: Could not find script at path '{script_path}' to patch.")
end

