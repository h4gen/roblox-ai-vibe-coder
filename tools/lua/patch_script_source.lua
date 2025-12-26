local target, err = SafeResolve(args.script_path)
if target and target:IsA("LuaSourceContainer") then
    local oldSource = target.Source
    local search = args.search_string
    local replace = args.replace_string
    
    -- Use string.find with 'true' for literal search (no patterns)
    local startIdx, endIdx = string.find(oldSource, search, 1, true)
    if startIdx then
        local newSource = string.sub(oldSource, 1, startIdx - 1) .. replace .. string.sub(oldSource, endIdx + 1)
        -- Syntax Check
        local func, compileErr = loadstring(newSource)
        if not func then
             return "Error: Syntax error in patched source code. Change NOT applied.\n" .. tostring(compileErr)
        else
            target.Source = newSource
            return "Successfully patched script: " .. target:GetFullName()
        end
    else
        return "Error: Search string not found in script (literal match failed)."
    end
else
    return "Error: Could not find script at path '" .. tostring(args.script_path) .. "' to patch. " .. (err or "")
end
