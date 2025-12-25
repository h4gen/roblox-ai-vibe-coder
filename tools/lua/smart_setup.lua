local InsertService = game:GetService("InsertService")
local MarketplaceService = game:GetService("MarketplaceService")
local query = "{query}"
local posStr = "{position}"

local function toVec3(s)
    local x,y,z = s:match("([^,]+),([^,]+),([^,]+)")
    if not x then return Vector3.new(0,5,0) end
    return Vector3.new(tonumber(x), tonumber(y), tonumber(z))
end

local function getGround(pos)
    local params = RaycastParams.new()
    params.FilterDescendantsInstances = {workspace:FindFirstChild("Baseplate")}
    params.FilterType = Enum.RaycastFilterType.Include
    local ray = workspace:Raycast(pos + Vector3.new(0, 50, 0), Vector3.new(0, -100, 0), params)
    if not ray then
        ray = workspace:Raycast(pos + Vector3.new(0, 50, 0), Vector3.new(0, -100, 0))
    end
    return ray and ray.Position or pos
end

print("--- Smart Asset Setup: " .. query .. " ---")

local success, result = pcall(function()
    local search = InsertService:GetFreeModels(query, 0)
    if not search then error("Marketplace search returned nil for query: " .. query) end
    
    local items = {}
    if type(search) == "table" then
        if search.Results then items = search.Results
        elseif search[1] and search[1].Results then items = search[1].Results
        else items = search end
    elseif type(search) == "userdata" and search.GetCurrentPage then
        items = search:GetCurrentPage()
    end
    
    -- Robust key detection for the first item
    local firstItem = (type(items) == "table" and items[1]) or (type(items) == "table" and items) or {}
    local assetId = firstItem.AssetId or firstItem.AssetID or firstItem.Id or firstItem.ID
    
    if not assetId then
        error("Smart Setup: No valid Asset ID found in search results for '" .. query .. "'.")
    end
    
    local model = InsertService:LoadAsset(assetId)
    model.Parent = workspace
    
    local targetPos = toVec3(posStr)
    -- Auto-grounding: search for surface
    local groundedPos = getGround(targetPos)
    model:MoveTo(groundedPos)
    model:MakeJoints()
    
    local payload = nil
    local category = "Unknown"
    
    -- Handle Kit Installers (Ungroup in X)
    for _, item in ipairs(model:GetDescendants()) do
        if item.Name == "Ungroup in Workspace" then
            for _, child in ipairs(item:GetChildren()) do child.Parent = workspace end
            item:Destroy()
        elseif item.Name == "Ungroup in ReplicatedStorage" then
            for _, child in ipairs(item:GetChildren()) do child.Parent = game:GetService("ReplicatedStorage") end
            item:Destroy()
        elseif item.Name == "Ungroup in ServerStorage" then
            for _, child in ipairs(item:GetChildren()) do child.Parent = game:GetService("ServerStorage") end
            item:Destroy()
        elseif item.Name == "Ungroup in ServerScriptService" then
            for _, child in ipairs(item:GetChildren()) do child.Parent = game:GetService("ServerScriptService") end
            item:Destroy()
        elseif item.Name == "Ungroup in StarterPack" then
            for _, child in ipairs(item:GetChildren()) do child.Parent = game:GetService("StarterPack") end
            item:Destroy()
        end
    end
    
    -- Scan for Tools
    for _, item in ipairs(model:GetDescendants()) do
        if item:IsA("Tool") then
            item.Parent = game:GetService("StarterPack")
            payload = item
            category = "Weapon/Tool"
            break
        end
    end
    
    -- Scan for NPCs
    if not payload then
        for _, item in ipairs(model:GetDescendants()) do
            if item:IsA("Humanoid") then
                local npc = item.Parent
                npc.Parent = game:GetService("ServerStorage")
                payload = npc
                category = "NPC"
                break
            end
        end
    end
    
    local finalPath = payload and payload:GetFullName() or model:GetFullName()
    print("Successfully setup " .. category .. " at " .. finalPath)
    
    -- Cleanup empty wrapper if payload was moved
    if payload and payload.Parent ~= model then
        model:Destroy()
    end
    
    return finalPath
end)

if not success then
    print("Error in smart setup: " .. tostring(result))
end

