local StudioService = game:GetService("StudioService")
if game.PlaceId == 0 then
    print("Error: This place is not published yet. Please File > Publish once manually.")
else
    local success, err = pcall(function()
        StudioService:PublishToRoblox()
    end)
    if success then
        print("Successfully Published! Place ID: " .. game.PlaceId)
    else
        print("Publish failed: " .. tostring(err))
    end
end

