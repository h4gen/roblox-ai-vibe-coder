local StudioService = game:GetService("StudioService")
if game.PlaceId == 0 then
    return "Error: This place is not published yet. Please File > Publish once manually."
else
    local success, err = pcall(function()
        StudioService:PublishToRoblox()
    end)
    if success then
        return "Successfully Published! Place ID: " .. game.PlaceId
    else
        return "Publish failed: " .. tostring(err)
    end
end
