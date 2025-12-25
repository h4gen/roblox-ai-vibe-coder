local RunService = game:GetService("RunService")
local state = "UNKNOWN"

if RunService:IsRunning() then
    if RunService:IsClient() then state = "PLAY_MODE (CLIENT)"
    elseif RunService:IsServer() then state = "PLAY_MODE (SERVER)"
    else state = "PLAY_MODE" end
else
    state = "EDIT_MODE"
end

print("--- Studio State ---")
print("Mode: " .. state)
print("PlaceId: " .. game.PlaceId)
print("UniverseId: " .. game.GameId)
if state == "EDIT_MODE" then
    print("TIP: Some objects (like zombies from spawners) only exist in PLAY_MODE.")
end

