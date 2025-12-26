local path, pathErr = SafeResolve(args.path)
local count = args.count or 10
local radius = args.radius or 100
local alignToSurface = args.align_to_surface == true
local randomRot = args.random_rotation ~= false

if not path then 
    return "Error: Source object for scattering not found. " .. (pathErr or "")
end

local function getGround(pos)
    local params = RaycastParams.new()
    local excludes = {path}
    for _, v in ipairs(workspace:GetDescendants()) do
        if v:IsA("BasePart") and (v.Transparency >= 0.5 or not v.CanCollide or v.Name:lower():find("mist") or v.Name:lower():find("fog") or v.Name:lower():find("effect")) then
            table.insert(excludes, v)
        end
    end
    params.FilterDescendantsInstances = excludes
    params.FilterType = Enum.RaycastFilterType.Exclude
    
    local result = workspace:Raycast(pos + Vector3.new(0, 1000, 0), Vector3.new(0, -2000, 0), params)
    if not result or (math.abs(result.Position.Y) < 0.001) then
        for i = 1, 3 do
            local offset = Vector3.new(math.random(-2,2), 0, math.random(-2,2))
            local retry = workspace:Raycast(pos + offset + Vector3.new(0, 1000, 0), Vector3.new(0, -2000, 0), params)
            if retry and math.abs(retry.Position.Y) > 0.001 then return retry end
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
        
        local ray = getGround(Vector3.new(x, 0, z))
        local groundPos = ray and ray.Position or Vector3.new(x, 0, z)
        local normal = ray and ray.Normal or Vector3.new(0, 1, 0)
        local finalCFrame = CFrame.new(groundPos)
        
        if randomRot then
            finalCFrame = finalCFrame * CFrame.Angles(0, math.rad(math.random(0, 360)), 0)
        end

        if alignToSurface then
            local currentUp = finalCFrame.UpVector
            local axis = currentUp:Cross(normal)
            if axis.Magnitude > 0.001 then
                local angle = math.acos(currentUp:Dot(normal))
                finalCFrame = CFrame.fromAxisAngle(axis, angle) * finalCFrame.Rotation + finalCFrame.Position
            end
            
            if clone:IsA("Model") then
                local _, s = clone:GetBoundingBox()
                finalCFrame = finalCFrame * CFrame.new(0, s.Y / 2, 0)
            else
                finalCFrame = finalCFrame * CFrame.new(0, clone.Size.Y / 2, 0)
            end
        else
            local height = clone:IsA("Model") and clone:GetExtentsSize().Y or clone.Size.Y
            local embedAmount = math.max(0.5, height * 0.1)
            finalCFrame = finalCFrame * CFrame.new(0, (height / 2) - embedAmount, 0)
        end

        if clone:IsA("Model") then clone:PivotTo(finalCFrame) else clone.CFrame = finalCFrame end
    end
end)

if success then
    return "Scattering complete."
else
    return "Error during scattering: " .. tostring(err)
end
