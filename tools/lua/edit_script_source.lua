local target, err = SafeResolve(args.script_path)
if target and target:IsA("LuaSourceContainer") then
    local newSource = args.new_source
    -- Basic Syntax Check
    local func, compileErr = loadstring(newSource)
    if not func then
        return "Error: Syntax error in new source code. Change NOT applied.\n" .. tostring(compileErr)
    else
        target.Source = newSource
        return "Successfully updated script: " .. target:GetFullName()
    end
else
    return "Error: Could not find script at path '" .. tostring(args.script_path) .. "' to edit. " .. (err or "")
end
