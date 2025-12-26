local template = {template_path}
local containerName = "{container_name}"
local interval = {interval}
local maxCount = {max_count}
local centerStr = "{spawn_area_center}"
local radius = {spawn_radius}

if not template then 
    print("Error: Template for spawner not found at path.") 
    return 
end

local function toVec3(s)
    local x,y,z = s:match("([^,]+),([^,]+),([^,]+)")
    return Vector3.new(tonumber(x), tonumber(y), tonumber(z))
end

local center = toVec3(centerStr)

local success, err = pcall(function()
    local folder = workspace:FindFirstChild(containerName)
    if not folder then
        folder = Instance.new("Folder")
        folder.Name = containerName
        folder.Parent = workspace
    end
    
    local spawnerScript = Instance.new("Script")
    spawnerScript.Name = containerName .. "_Spawner"
    
    -- Robustly determine service and name
    local serviceName = "ServerStorage"
    if template:IsDescendantOf(game.ReplicatedStorage) then
        serviceName = "ReplicatedStorage"
    elseif template:IsDescendantOf(workspace) then
        serviceName = "Workspace"
    end
    
    local templateName = template.Name
    
    spawnerScript.Source = string.format([[
        local service = game:GetService("%s")
        local template = service:WaitForChild("%s")
        local folder = workspace:WaitForChild("%s")
        local interval = %f
        local maxCount = %d
        local center = Vector3.new(%f, %f, %f)
        local radius = %f
        
        while true do
            task.wait(interval)
            if #folder:GetChildren() < maxCount then
                local clone = template:Clone()
                local x = center.X + (math.random() - 0.5) * radius * 2
                local z = center.Z + (math.random() - 0.5) * radius * 2
                clone.Parent = folder
                
                -- ROBUSTNESS FIX: Ensure PrimaryPart
                if clone:IsA("Model") and not clone.PrimaryPart then
                    clone.PrimaryPart = clone:FindFirstChild("HumanoidRootPart") or clone:FindFirstChild("Torso") or clone:FindFirstChildWhichIsA("BasePart")
                end

                if clone:IsA("Model") then
                    if clone.PrimaryPart then
                        clone:SetPrimaryPartCFrame(CFrame.new(Vector3.new(x, center.Y + 50, z)))
                    else
                        clone:MoveTo(Vector3.new(x, center.Y + 50, z))
                    end
                else
                    clone.Position = Vector3.new(x, center.Y + 50, z)
                end
                
                -- Simple ground detection
                local ray = workspace:Raycast(Vector3.new(x, center.Y + 100, z), Vector3.new(0, -200, 0))
                if ray then
                    if clone:IsA("Model") then 
                        if clone.PrimaryPart then
                             clone:SetPrimaryPartCFrame(CFrame.new(ray.Position + Vector3.new(0, clone:GetExtentsSize().Y/2, 0)))
                        else
                             clone:MoveTo(ray.Position) 
                        end
                    else 
                        clone.Position = ray.Position + Vector3.new(0, clone.Size.Y/2, 0)
                    end
                end
            end
        end
    ]], serviceName, templateName, containerName, interval, maxCount, center.X, center.Y, center.Z, radius)
    
    spawnerScript.Parent = workspace
end)

if success then
    print("Successfully created spawner: " .. containerName .. "_Spawner")
else
    print("Error creating spawner: " .. tostring(err))
end
