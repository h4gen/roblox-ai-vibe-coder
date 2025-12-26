local RunService = game:GetService("RunService")
local state = "UNKNOWN"

if RunService:IsRunning() then
    if RunService:IsClient() then state = "PLAY_MODE (CLIENT)"
    elseif RunService:IsServer() then state = "PLAY_MODE (SERVER)"
    else state = "PLAY_MODE" end
else
    state = "EDIT_MODE"
end

local res = "--- Studio State ---\n"
res = res .. "Mode: " .. state .. "\n"
res = res .. "PlaceId: " .. game.PlaceId .. "\n"
res = res .. "UniverseId: " .. game.GameId .. "\n"
if state == "EDIT_MODE" then
    res = res .. "TIP: Some objects (like zombies from spawners) only exist in PLAY_MODE.\n"
end
return res
