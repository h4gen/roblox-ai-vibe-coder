local InsertService = game:GetService("InsertService")
local query = args.query

local success, result = pcall(function()
    return InsertService:GetFreeModels(query, 0)
end)

if success then
    if result then
        local items = {}
        if type(result) == "table" then
            if result.Results then items = result.Results
            elseif result[1] and result[1].Results then items = result[1].Results
            else items = result end
        elseif type(result) == "userdata" and result.GetCurrentPage then
            items = result:GetCurrentPage()
        end

        if not items or #items == 0 or (type(items) == "table" and #items >= 1 and items[1] == nil) then
            return "0 results found for '" .. tostring(query) .. "'. TIP: Try broader keywords."
        else
            local output = "--- Marketplace Search Results for '" .. tostring(query) .. "' ---\n"
            local count = 0
            for i = 1, #items do
                local item = items[i]
                if item and (item.Name or item.AssetId) then
                    count = count + 1
                    local id = item.AssetId or item.AssetID or item.Id or item.ID
                    output = output .. count .. ". " .. tostring(item.Name or "Unknown") .. " (Creator: " .. tostring(item.CreatorName or "Unknown") .. ", AssetID: " .. tostring(id) .. ")\n"
                    if count >= 5 then break end
                end
            end
            if count == 0 then return "0 results found for '" .. tostring(query) .. "'." end
            return output
        end
    else
        return "Error: Marketplace search returned nil result."
    end
else
    return "Error searching marketplace: " .. tostring(result)
end
