local parentPath = "{parent_path}"
local layoutType = "{layout_type}" -- "ScreenGui", "CenteredModal", "GridMenu", "HUD"
local name = "{name}"

local function getParent()
    if parentPath == "game.StarterGui" or parentPath == "StarterGui" then
        return game:GetService("StarterGui")
    end
    -- Try to find object by path
    local segments = {}
    for part in string.gmatch(parentPath, "[^%.]+") do
        table.insert(segments, part)
    end
    
    local current = game
    for i, seg in ipairs(segments) do
        if i == 1 and seg == "game" then continue end
        if current then
            current = current:FindFirstChild(seg)
        end
    end
    return current
end

local parent = getParent()
if not parent then
    return "Error: Parent not found at " .. parentPath
end

local root
if layoutType == "ScreenGui" then
    root = Instance.new("ScreenGui")
    root.Name = name
    root.ResetOnSpawn = false
    root.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    root.Parent = parent
    return root:GetFullName()
end

-- For other types, we might need a ScreenGui container if parent is StarterGui
if parent:IsA("StarterGui") or parent:IsA("PlayerGui") then
    -- Create a wrapper ScreenGui
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
    -- Center of screen, 50% width, 70% height
    mainFrame.Size = UDim2.new(0.5, 0, 0.7, 0)
    mainFrame.Position = UDim2.new(0.5, 0, 0.5, 0)
    mainFrame.AnchorPoint = Vector2.new(0.5, 0.5)
    
    -- Add AspectRatioConstraint to keep it from getting too wide/tall
    local arc = Instance.new("UIAspectRatioConstraint")
    arc.AspectRatio = 1.3
    arc.AspectType = Enum.AspectType.FitWithinMaxSize
    arc.DominantAxis = Enum.DominantAxis.Width
    arc.Parent = mainFrame
    
    -- Add UICorner
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 12)
    corner.Parent = mainFrame
    
    -- Add Title
    local title = Instance.new("TextLabel")
    title.Name = "Title"
    title.Text = name
    title.Size = UDim2.new(1, 0, 0.1, 0)
    title.BackgroundTransparency = 1
    title.TextColor3 = Color3.new(1, 1, 1)
    title.Font = Enum.Font.GothamBold
    title.TextScaled = true
    title.Parent = mainFrame
    
elseif layoutType == "GridMenu" then
    -- A scrolling grid (like an inventory)
    mainFrame.Size = UDim2.new(0.6, 0, 0.6, 0)
    mainFrame.Position = UDim2.new(0.5, 0, 0.5, 0)
    mainFrame.AnchorPoint = Vector2.new(0.5, 0.5)
    mainFrame.BackgroundTransparency = 0.1
    
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 8)
    corner.Parent = mainFrame
    
    -- Scroll Container
    local scroll = Instance.new("ScrollingFrame")
    scroll.Name = "Container"
    scroll.Size = UDim2.new(1, -20, 1, -20)
    scroll.Position = UDim2.new(0, 10, 0, 10)
    scroll.BackgroundTransparency = 1
    scroll.BorderSizePixel = 0
    scroll.ScrollBarThickness = 6
    scroll.AutomaticCanvasSize = Enum.AutomaticSize.Y
    scroll.CanvasSize = UDim2.new(0,0,0,0) -- Let automatic handle it
    scroll.Parent = mainFrame
    
    local grid = Instance.new("UIGridLayout")
    grid.CellSize = UDim2.new(0.3, 0, 0, 100) -- Will need AspectRatio on children
    grid.CellPadding = UDim2.new(0.03, 0, 0, 10)
    grid.Parent = scroll
    
    local pad = Instance.new("UIPadding")
    pad.PaddingTop = UDim.new(0, 10)
    pad.PaddingBottom = UDim.new(0, 10)
    pad.PaddingLeft = UDim.new(0, 10)
    pad.PaddingRight = UDim.new(0, 10)
    pad.Parent = scroll
    
elseif layoutType == "HUD" then
    -- Bottom left stats
    mainFrame.Size = UDim2.new(0.2, 0, 0.15, 0)
    mainFrame.Position = UDim2.new(0, 20, 1, -20)
    mainFrame.AnchorPoint = Vector2.new(0, 1)
    mainFrame.BackgroundTransparency = 0.5
    
    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 8)
    corner.Parent = mainFrame
    
    local list = Instance.new("UIListLayout")
    list.Padding = UDim.new(0, 5)
    list.SortOrder = Enum.SortOrder.LayoutOrder
    list.Parent = mainFrame
    
    local pad = Instance.new("UIPadding")
    pad.PaddingTop = UDim.new(0, 10)
    pad.PaddingBottom = UDim.new(0, 10)
    pad.PaddingLeft = UDim.new(0, 10)
    pad.Parent = mainFrame
end

print("Created UI Layout: " .. layoutType .. " at " .. mainFrame:GetFullName())
return mainFrame:GetFullName()
