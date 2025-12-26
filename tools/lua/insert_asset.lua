local InsertService = game:GetService("InsertService")
local assetId = {asset_id}
local posStr = "{position}"

local function toVec3(s)
    local x,y,z = s:match("([^,]+),([^,]+),([^,]+)")
    return Vector3.new(tonumber(x), tonumber(y), tonumber(z))
end

local function loadAsset(id)
    local s, m = pcall(function() return InsertService:LoadAsset(id) end)
    if s and m then return m end
    
    local s2, objects = pcall(function() return game:GetObjects("rbxassetid://" .. id) end)
    if s2 and objects and objects[1] then
        return objects[1]
    end
    return nil, m or "Unknown error"
end

local model, err = loadAsset(assetId)

if model then
    model.Parent = workspace
    model:MoveTo(toVec3(posStr))
    model:MakeJoints()
    print("Successfully inserted and placed asset " .. assetId .. " at " .. posStr)
else
    print("Error inserting asset: " .. tostring(err))
end

