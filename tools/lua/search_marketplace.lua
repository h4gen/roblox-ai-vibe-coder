local InsertService = game:GetService("InsertService")
local query = "{query}"

local success, result = pcall(function()
    return InsertService:GetFreeModels(query, 0)
end)

local output = "--- Marketplace Search Results for '" .. query .. "' ---\n"

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

        if not items or #items == 0 then
            print("0 results found for '" .. query .. "'. \nTIP: Try broader 1-2 word keywords.")
        else
            for i = 1, math.min(5, #items) do
                local item = items[i]
                local id = item.AssetId or item.AssetID or item.Id or item.ID
                output = output .. i .. ". " .. item.Name .. " (Creator: " .. (item.CreatorName or "Unknown") .. ", AssetID: " .. tostring(id) .. ")\n"
            end
            print(output)
        end
    else
        print("Error: Marketplace search returned nil result.")
    end
else
    print("Error searching marketplace: " .. tostring(result))
end

