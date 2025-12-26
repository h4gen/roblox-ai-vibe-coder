local path = "{path}"
local templateName = "{template_name}" -- "Leaderstats", "TouchKill", "ClickDoor", "AutoRotate"

local function getScript()
    local segments = {{}}
    for part in string.gmatch(path, "[^%.]+") do
        table.insert(segments, part)
    end
    local current = game
    for i, seg in ipairs(segments) do
        if i == 1 and seg == "game" then continue end
        if current then current = current:FindFirstChild(seg) end
    end
    return current
end

local targetScript = getScript()
if not targetScript or not (targetScript:IsA("Script") or targetScript:IsA("LocalScript") or targetScript:IsA("ModuleScript")) then
    return "Error: Script not found or invalid at " .. path
end

local templates = {{}}

templates.Leaderstats = [[
local Players = game:GetService("Players")

local function onPlayerAdded(player)
    local leaderstats = Instance.new("Folder")
    leaderstats.Name = "leaderstats"
    leaderstats.Parent = player

    local gold = Instance.new("IntValue")
    gold.Name = "Gold"
    gold.Value = 0
    gold.Parent = leaderstats

    local xp = Instance.new("IntValue")
    xp.Name = "XP"
    xp.Value = 0
    xp.Parent = leaderstats
    
    -- Load data here if needed using DataStoreService
end

Players.PlayerAdded:Connect(onPlayerAdded)
]]

templates.TouchKill = [[
local part = script.Parent

local function onTouch(otherPart)
    local character = otherPart.Parent
    local humanoid = character:FindFirstChild("Humanoid")
    if humanoid then
        humanoid.Health = 0
    end
end

part.Touched:Connect(onTouch)
]]

templates.ClickDoor = [[
local TweenService = game:GetService("TweenService")
local door = script.Parent
local clickDetector = door:FindFirstChild("ClickDetector") or Instance.new("ClickDetector", door)

local isOpen = false
local closedCFrame = door.CFrame
local openCFrame = door.CFrame * CFrame.Angles(0, math.rad(90), 0)

local tweenInfo = TweenInfo.new(1, Enum.EasingStyle.Bounce)
local openTween = TweenService:Create(door, tweenInfo, {{CFrame = openCFrame}})
local closeTween = TweenService:Create(door, tweenInfo, {{CFrame = closedCFrame}})

clickDetector.MouseClick:Connect(function()
    if isOpen then
        closeTween:Play()
    else
        openTween:Play()
    end
    isOpen = not isOpen
end)
]]

templates.AutoRotate = [[
local RunService = game:GetService("RunService")
local part = script.Parent

local ROTATION_SPEED = 90 -- Degrees per second

RunService.Heartbeat:Connect(function(dt)
    part.CFrame = part.CFrame * CFrame.Angles(0, math.rad(ROTATION_SPEED * dt), 0)
end)
]]

if not templates[templateName] then
    return "Error: Template '" .. templateName .. "' not found."
end

targetScript.Source = templates[templateName]
return "Success: Injected " .. templateName .. " into " .. path
