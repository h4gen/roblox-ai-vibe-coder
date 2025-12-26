local parent, err = SafeResolve(args.parent_path)
local layoutType = args.layout_type
local name = args.name

if not parent then return "Error: Parent not found. " .. (err or "") end

if layoutType == "ScreenGui" then
    local root = Instance.new("ScreenGui")
    root.Name = name
    root.ResetOnSpawn = false
    root.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    root.Parent = parent
    return root:GetFullName()
end

if parent:IsA("StarterGui") or parent:IsA("PlayerGui") then
    local sg = Instance.new("ScreenGui")
    sg.Name = name .. "_Gui"
    sg.ResetOnSpawn = false
    sg.Parent = parent
    parent = sg
end

local mainFrame = Instance.new("Frame")
mainFrame.Name = name
mainFrame.BackgroundColor3 = Color3.fromRGB(45, 45, 45)
mainFrame.BorderSizePixel = 0
mainFrame.Parent = parent

if layoutType == "CenteredModal" then
    mainFrame.Size = UDim2.new(0.5, 0, 0.7, 0)
    mainFrame.Position = UDim2.new(0.5, 0, 0.5, 0)
    mainFrame.AnchorPoint = Vector2.new(0.5, 0.5)
    local arc = Instance.new("UIAspectRatioConstraint", mainFrame)
    arc.AspectRatio = 1.3
    Instance.new("UICorner", mainFrame).CornerRadius = UDim.new(0, 12)
    local title = Instance.new("TextLabel", mainFrame)
    title.Name = "Title"
    title.Text = name
    title.Size = UDim2.new(1, 0, 0.1, 0)
    title.BackgroundTransparency = 1
    title.TextColor3 = Color3.new(1, 1, 1)
    title.Font = Enum.Font.GothamBold
    title.TextScaled = true
elseif layoutType == "GridMenu" then
    mainFrame.Size = UDim2.new(0.6, 0, 0.6, 0)
    mainFrame.Position = UDim2.new(0.5, 0, 0.5, 0)
    mainFrame.AnchorPoint = Vector2.new(0.5, 0.5)
    Instance.new("UICorner", mainFrame).CornerRadius = UDim.new(0, 8)
    local scroll = Instance.new("ScrollingFrame", mainFrame)
    scroll.Name = "Container"
    scroll.Size = UDim2.new(1, -20, 1, -20)
    scroll.Position = UDim2.new(0, 10, 0, 10)
    scroll.BackgroundTransparency = 1
    scroll.AutomaticCanvasSize = Enum.AutomaticSize.Y
    Instance.new("UIGridLayout", scroll).CellSize = UDim2.new(0.3, 0, 0, 100)
elseif layoutType == "HUD" then
    mainFrame.Size = UDim2.new(0.2, 0, 0.15, 0)
    mainFrame.Position = UDim2.new(0, 20, 1, -20)
    mainFrame.AnchorPoint = Vector2.new(0, 1)
    mainFrame.BackgroundTransparency = 0.5
    Instance.new("UICorner", mainFrame).CornerRadius = UDim.new(0, 8)
    Instance.new("UIListLayout", mainFrame).Padding = UDim.new(0, 5)
end

return "Created UI Layout: " .. layoutType .. " at " .. mainFrame:GetFullName()
