local code = args.code or args.command
if not code or code == "" then return "Error: No code provided to run_code." end

local func, compileErr = loadstring(code)
if not func then
    return "Syntax Error in run_code: " .. tostring(compileErr)
end

-- Use the same environment as the plugin
setfenv(func, getfenv())

local success, runtimeResult = pcall(func)
if success then
    return runtimeResult
else
    return "Runtime Error in run_code: " .. tostring(runtimeResult)
end

