local target, err = SafeResolve(args.path)
local templateName = args.template_name

if not target or not target:IsA("LuaSourceContainer") then
    return "Error: Script not found or invalid at path. " .. (err or "")
end

local templates = {
    Leaderstats = [[
local Players = game:GetService("Players")
local function onPlayerAdded(player)
    local leaderstats = Instance.new("Folder")
    leaderstats.Name = "leaderstats"
    leaderstats.Parent = player
    local gold = Instance.new("IntValue")
    gold.Name = "Gold"
    gold.Value = 0
    gold.Parent = leaderstats
end
Players.PlayerAdded:Connect(onPlayerAdded)
]],
    TouchKill = [[
local part = script.Parent
local function onTouch(otherPart)
    local character = otherPart.Parent
    local humanoid = character:FindFirstChild("Humanoid")
    if humanoid then humanoid.Health = 0 end
end
part.Touched:Connect(onTouch)
]],
    ClickDoor = [[
local TweenService = game:GetService("TweenService")
local door = script.Parent
local clickDetector = door:FindFirstChild("ClickDetector") or Instance.new("ClickDetector", door)
local isOpen = false
local closedCFrame = door.CFrame
local openCFrame = door.CFrame * CFrame.Angles(0, math.rad(90), 0)
local tweenInfo = TweenInfo.new(1, Enum.EasingStyle.Bounce)
local openTween = TweenService:Create(door, tweenInfo, {CFrame = openCFrame})
local closeTween = TweenService:Create(door, tweenInfo, {CFrame = closedCFrame})
clickDetector.MouseClick:Connect(function()
    if isOpen then closeTween:Play() else openTween:Play() end
    isOpen = not isOpen
end)
]],
    AutoRotate = [[
local RunService = game:GetService("RunService")
local part = script.Parent
local ROTATION_SPEED = 90
RunService.Heartbeat:Connect(function(dt)
    part.CFrame = part.CFrame * CFrame.Angles(0, math.rad(ROTATION_SPEED * dt), 0)
end)
]]
}

if not templates[templateName] then
    return "Error: Template '" .. tostring(templateName) .. "' not found."
end

target.Source = templates[templateName]
return "Success: Injected " .. templateName .. " into " .. target:GetFullName()
