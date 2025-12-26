local path = {path}
local count = {count}
local radius = {radius}
local alignToSurface = {align_to_surface}
local randomRot = {random_rotation}

-- Wait for source object if it's not immediately available (handles marketplace delay)
local function waitForObject(objPath, timeout)
    local start = tick()
    while not objPath and (tick() - start) < (timeout or 5) do
        task.wait(0.5)
    end
    return objPath
end

if not path then 
    print("Error: Source object for scattering not found. Please verify the path.") 
    return 
end

print("--- Scattering " .. count .. " instances of " .. path.Name .. " ---")

local function getGround(pos)
    local params = RaycastParams.new()
    
    -- SMART FILTER: Exclude the object itself and any parts that are likely just "effects"
    local excludes = {{path}}
    for _, v in ipairs(workspace:GetDescendants()) do
        if v:IsA("BasePart") and (v.Transparency >= 0.5 or not v.CanCollide or v.Name:lower():find("mist") or v.Name:lower():find("fog") or v.Name:lower():find("effect")) then
            table.insert(excludes, v)
        end
    end
    params.FilterDescendantsInstances = excludes
    params.FilterType = Enum.RaycastFilterType.Exclude
    
    -- Cast from higher up to ensure we hit even high mountains
    local result = workspace:Raycast(pos + Vector3.new(0, 1000, 0), Vector3.new(0, -2000, 0), params)
    
    -- RETRY LOGIC: If we hit Y=0 and it's suspiciously flat, try a few offsets
    if not result or (math.abs(result.Position.Y) < 0.001) then
        for i = 1, 3 do
            local offset = Vector3.new(math.random(-2,2), 0, math.random(-2,2))
            local retry = workspace:Raycast(pos + offset + Vector3.new(0, 1000, 0), Vector3.new(0, -2000, 0), params)
            if retry and math.abs(retry.Position.Y) > 0.001 then
                return retry
            end
        end
    end

    return result
end

local success, err = pcall(function()
    for i = 1, count do
        local clone = path:Clone()
        local x = (math.random() - 0.5) * radius * 2
        local z = (math.random() - 0.5) * radius * 2
        
        clone.Parent = workspace
        
        -- 1. Find ground
        local ray = getGround(Vector3.new(x, 0, z))
        local groundPos = ray and ray.Position or Vector3.new(x, 0, z)
        local normal = ray and ray.Normal or Vector3.new(0, 1, 0)
        
        -- 2. Calculate Orientation and Embed
        local finalCFrame = CFrame.new(groundPos)
        
        if randomRot then
            finalCFrame = finalCFrame * CFrame.Angles(0, math.rad(math.random(0, 360)), 0)
        end

        if alignToSurface then
            -- TILT logic (e.g. debris, skateboards)
            local currentUp = finalCFrame.UpVector
            local axis = currentUp:Cross(normal)
            if axis.Magnitude > 0.001 then
                local angle = math.acos(currentUp:Dot(normal))
                finalCFrame = CFrame.fromAxisAngle(axis, angle) * finalCFrame.Rotation + finalCFrame.Position
            end
            
            -- Sit ON TOP
            if clone:IsA("Model") then
                local _, size = clone:GetBoundingBox()
                finalCFrame = finalCFrame * CFrame.new(0, size.Y / 2, 0)
            else
                finalCFrame = finalCFrame * CFrame.new(0, clone.Size.Y / 2, 0)
            end
        else
            -- UPRIGHT & EMBED logic (e.g. Trees, Crypts)
            local height = 0
            if clone:IsA("Model") then
                local _, size = clone:GetBoundingBox()
                height = size.Y
            else
                height = clone.Size.Y
            end
            
            -- Sink slightly into the ground to ensure no floating edges on slopes
            local embedAmount = math.max(0.5, height * 0.1)
            finalCFrame = finalCFrame * CFrame.new(0, (height / 2) - embedAmount, 0)
        end

        -- 3. Apply final placement
        if clone:IsA("Model") then
            clone:PivotTo(finalCFrame)
        else
            clone.CFrame = finalCFrame
        end
    end
end)

if success then
    print("Scattering complete.")
else
    print("Error during scattering: " .. tostring(err))
end
