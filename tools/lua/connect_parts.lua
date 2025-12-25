local partA = {part_a}
local partB = {part_b}
local type = "{constraint_type}"
local axis = "{axis}" -- X, Y, Z
local mode = "{anchor_mode}" -- Center, ClosestPoint

if not partA or not partB then print("Error: One or both parts not found.") return end
if not partA:IsA("BasePart") or not partB:IsA("BasePart") then print("Error: Both targets must be BaseParts.") return end

-- 1. Create Attachments
local att0 = Instance.new("Attachment")
att0.Name = "Att_" .. type
att0.Parent = partA

local att1 = Instance.new("Attachment")
att1.Name = "Att_" .. type
att1.Parent = partB

-- 2. Position Attachments (Smart Alignment)
if mode == "Center" then
    -- Default: Snap to center of each part
    att0.Position = Vector3.new(0,0,0)
    -- Align Att1 to match Att0's world position relative to Part A
    att1.CFrame = partB.CFrame:Inverse() * partA.CFrame
else
    -- Closest Point (Basic approximation)
    local dist = (partB.Position - partA.Position).Magnitude
    local dir = (partB.Position - partA.Position).Unit
    att0.WorldPosition = partA.Position + (dir * (math.min(partA.Size.X, partA.Size.Z)/2))
    att1.WorldPosition = att0.WorldPosition -- Snap together
end

-- 3. Axis Alignment (For Hinges/Motors)
if type == "Hinge" or type == "Motor6D" or type == "Prismatic" then
    local axisVec = Vector3.new(0, 1, 0) -- Default Y
    if axis == "X" then axisVec = Vector3.new(1, 0, 0)
    elseif axis == "Z" then axisVec = Vector3.new(0, 0, 1) end
    
    att0.Axis = axisVec
    att1.Axis = axisVec
end

-- 4. Create the Constraint
local constraint = nil

if type == "Weld" then
    constraint = Instance.new("WeldConstraint")
    constraint.Part0 = partA
    constraint.Part1 = partB
    -- WeldConstraints don't use attachments, they just lock current relative pos
    att0:Destroy()
    att1:Destroy()
elseif type == "Motor6D" then
    constraint = Instance.new("Motor6D")
    constraint.Part0 = partA
    constraint.Part1 = partB
    constraint.C0 = att0.CFrame
    constraint.C1 = att1.CFrame
    -- Cleanup attachments as Motor6D uses C0/C1 internal properties
    att0:Destroy()
    att1:Destroy()
else
    -- Standard Constraints (Hinge, BallSocket, etc.)
    constraint = Instance.new(type .. "Constraint")
    constraint.Attachment0 = att0
    constraint.Attachment1 = att1
end

constraint.Name = "Connection_" .. partB.Name
constraint.Parent = partA

-- Safely set Visible property if it exists
pcall(function() constraint.Visible = true end)

print("Successfully connected " .. partA.Name .. " and " .. partB.Name .. " with " .. type)

