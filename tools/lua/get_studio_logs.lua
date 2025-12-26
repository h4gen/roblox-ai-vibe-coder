local LogService = game:GetService("LogService")
local logs = LogService:GetLogHistory()
local count = args.line_count or 50
local startIdx = math.max(1, #logs - count + 1)
local result = "--- Recent Studio Logs ---\n"
for i = startIdx, #logs do
    local log = logs[i]
    result = result .. "[" .. log.messageType.Name .. "] " .. log.message .. "\n"
end
return result
