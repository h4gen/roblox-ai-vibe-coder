local path = {path}
local count = {count}
local radius = {radius}
local alignToSurface = {align_to_surface}
local randomRot = {random_rotation}

if not path then 
    print("Error: Source object for scattering not found. Please verify the path.") 
    return 
end

print("--- Scattering " .. count .. " instances of " .. path.Name .. " ---")

local function getGround(pos)
    local params = RaycastParams.new()
    -- Safety check for filter
    if typeof(path) == "Instance" then
        params.FilterDescendantsInstances = {path} -- Don't hit self
    else
        print("Warning: Scatter source is not an Instance ("..typeof(path).."). Raycast filtering disabled for source.")
    end
    params.FilterType = Enum.RaycastFilterType.Exclude
    
    local ray = workspace:Raycast(pos + Vector3.new(0, 500, 0), Vector3.new(0, -1000, 0), params)
    return ray and ray.Position or (pos + Vector3.new(0, 500, 0)) -- Fallback if missed
end

local success, err = pcall(function()
    if typeof(path) ~= "Instance" then
        print("Warning: Path argument is not an Instance (" .. typeof(path) .. "). Attempting to proceed, but Raycast filter may be unsafe.")
    end

    for i = 1, count do
        local clone = path:Clone()
        local x = (math.random() - 0.5) * radius * 2
        local z = (math.random() - 0.5) * radius * 2
        
        clone.Parent = workspace
        
        local targetPos = Vector3.new(x, 0, z)
        
        if alignToSurface then
            targetPos = getGround(targetPos)
        end
        
        local targetCF = CFrame.new(targetPos)
        
        -- Adjust for model size to prevent sinking
        if clone:IsA("Model") then
            local _, size = clone:GetBoundingBox()
            targetCF = targetCF * CFrame.new(0, size.Y/2, 0)
        elseif clone:IsA("BasePart") then
            targetCF = targetCF * CFrame.new(0, clone.Size.Y/2, 0)
        end
        
        if randomRot then
            targetCF = targetCF * CFrame.Angles(0, math.rad(math.random(0, 360)), 0)
        end
        
        if clone:IsA("Model") then
            clone:PivotTo(targetCF)
        else
            clone.CFrame = targetCF
        end
    end
end)

if success then
    print("Scattering complete.")
else
    print("Error during scattering: " .. tostring(err))
end

