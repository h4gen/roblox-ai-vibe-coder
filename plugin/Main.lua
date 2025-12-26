local HttpService = game:GetService("HttpService")
local RunService = game:GetService("RunService")

-- Create the Toolbar
local Toolbar = plugin:CreateToolbar("Vibe Coder")

-- FIXED: Empty string icon to force default behavior
local Button = Toolbar:CreateButton(
	"Connect", 
	"Connect to Vibe Coder Cloud", 
	"" 
)

-- Configuration
local API_URL = "http://127.0.0.1:8000"
local USER_TOKEN = plugin:GetSetting("UserToken") or "test-token"

-- State
local isRunning = false
local pollRate = 1.0
local lastPoll = 0

local function ExecuteCommand(commandData)
	local code = commandData.code
	if not code or code == "" then return end

	print("[Vibe Coder] Executing...")
	local func, compileErr = loadstring(code)

	if not func then
		warn("[Vibe Coder] ❌ Syntax Error: " .. tostring(compileErr))
		return { success = false, error = tostring(compileErr) }
	end

	setfenv(func, getfenv())
	local success, runtimeResult = pcall(func)

	if success then
		print("[Vibe Coder] ✅ Success.")
		return { success = true, output = tostring(runtimeResult) }
	else
		warn("[Vibe Coder] ⚠️ Runtime Error: " .. tostring(runtimeResult))
		return { success = false, error = tostring(runtimeResult) }
	end
end

RunService.Heartbeat:Connect(function(dt)
	if not isRunning then return end

	lastPoll = lastPoll + dt
	if lastPoll < pollRate then return end
	lastPoll = 0

	local success, response = pcall(function()
		return HttpService:RequestAsync({
			Url = API_URL .. "/poll",
			Method = "POST",
			Headers = { ["Content-Type"] = "application/json" },
			Body = HttpService:JSONEncode({ status = "idle", place_id = game.PlaceId })
		})
	end)

	if success then
		if response.StatusCode == 200 then
			local data = HttpService:JSONDecode(response.Body)
			if data and data.command then
				local result = ExecuteCommand(data.command)
				pcall(function()
					HttpService:PostAsync(
						API_URL .. "/callback",
						HttpService:JSONEncode({ id = data.command.id, result = result })
					)
				end)
			end
		end
	else
		warn("[Vibe Coder] Connection failed: " .. tostring(response))
	end
end)

Button.Click:Connect(function()
	isRunning = not isRunning
	Button:SetActive(isRunning)
	if isRunning then
		print("🟢 Vibe Coder Listening on " .. API_URL)
		print("Make sure your Python server is running!")
	else
		print("🔴 Vibe Coder Paused.")
	end
end)