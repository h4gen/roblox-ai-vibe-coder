local InsertService = game:GetService("InsertService")
local assetId = {asset_id}
local posStr = "{position}"

local function toVec3(s)
    local x,y,z = s:match("([^,]+),([^,]+),([^,]+)")
    return Vector3.new(tonumber(x), tonumber(y), tonumber(z))
end

local success, model = pcall(function()
    return InsertService:LoadAsset(assetId)
end)

if success and model then
    model.Parent = workspace
    model:MoveTo(toVec3(posStr))
    model:MakeJoints()
    print("Successfully inserted and placed asset " .. assetId .. " at " .. posStr)
else
    print("Error inserting asset: " .. tostring(model))
end

