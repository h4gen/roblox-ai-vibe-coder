local template, templateErr = SafeResolve(args.template_path)
local containerName = args.container_name or "SpawnedObjects"
local interval = args.interval or 5
local maxCount = args.max_count or 10
local centerStr = args.spawn_area_center or "0,10,0"
local radius = args.spawn_radius or 100

if not template then 
    return "Error: Template for spawner not found. " .. (templateErr or "")
end

local function toVec3(s)
    if type(s) == "table" then return Vector3.new(s.x or s[1], s.y or s[2], s.z or s[3]) end
    local x,y,z = tostring(s):match("([^,]+),([^,]+),([^,]+)")
    return Vector3.new(tonumber(x or 0), tonumber(y or 0), tonumber(z or 0))
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
                
                if clone:IsA("Model") and not clone.PrimaryPart then
                    clone.PrimaryPart = clone:FindFirstChild("HumanoidRootPart") or clone:FindFirstChild("Torso") or clone:FindFirstChildWhichIsA("BasePart")
                end

                if clone:IsA("Model") then
                    if clone.PrimaryPart then
                        clone:PivotTo(CFrame.new(Vector3.new(x, center.Y + 50, z)))
                    else
                        clone:MoveTo(Vector3.new(x, center.Y + 50, z))
                    end
                else
                    clone.Position = Vector3.new(x, center.Y + 50, z)
                end
                
                local ray = workspace:Raycast(Vector3.new(x, center.Y + 100, z), Vector3.new(0, -200, 0))
                if ray then
                    if clone:IsA("Model") then 
                        if clone.PrimaryPart then
                             clone:PivotTo(CFrame.new(ray.Position + Vector3.new(0, clone:GetExtentsSize().Y/2, 0)))
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
    return "Successfully created spawner: " .. containerName .. "_Spawner"
else
    return "Error creating spawner: " .. tostring(err)
end
