local target = {script_path}
if target and (target:IsA("LuaSourceContainer")) then
    return target.Source
else
    return "Error: Script at '{script_path}' not found or is not a script container."
end

