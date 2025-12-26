local target, err = SafeResolve(args.script_path)
if target and target:IsA("LuaSourceContainer") then
    return target.Source
else
    return "Error: Script at '" .. tostring(args.script_path) .. "' not found or is not a script container. " .. (err or "")
end
