local target = {script_path}
if target and (target:IsA("LuaSourceContainer")) then
    print(target.Source)
else
    print("Error: Script at '{script_path}' not found or is not a script container.")
end

