local partA, errA = SafeResolve(args.part_a)
local partB, errB = SafeResolve(args.part_b)
local cType = args.constraint_type or "Weld"
local axis = args.axis or "Y"
local mode = args.anchor_mode or "Center"

if not partA or not partB then return "Error: One or both parts not found. " .. (errA or "") .. " " .. (errB or "") end
if not partA:IsA("BasePart") or not partB:IsA("BasePart") then return "Error: Both targets must be BaseParts." end

local att0 = Instance.new("Attachment")
att0.Name = "Att_" .. cType
att0.Parent = partA

local att1 = Instance.new("Attachment")
att1.Name = "Att_" .. cType
att1.Parent = partB

if mode == "Center" then
    att0.Position = Vector3.new(0,0,0)
    att1.CFrame = partB.CFrame:Inverse() * partA.CFrame
else
    local dir = (partB.Position - partA.Position).Unit
    att0.WorldPosition = partA.Position + (dir * (math.min(partA.Size.X, partA.Size.Z)/2))
    att1.WorldPosition = att0.WorldPosition
end

if cType == "Hinge" or cType == "Motor6D" or cType == "Prismatic" then
    local axisVec = Vector3.new(0, 1, 0)
    if axis == "X" then axisVec = Vector3.new(1, 0, 0)
    elseif axis == "Z" then axisVec = Vector3.new(0, 0, 1) end
    att0.Axis = axisVec
    att1.Axis = axisVec
end

local constraint = nil
if cType == "Weld" then
    constraint = Instance.new("WeldConstraint")
    constraint.Part0 = partA
    constraint.Part1 = partB
    att0:Destroy()
    att1:Destroy()
elseif cType == "Motor6D" then
    constraint = Instance.new("Motor6D")
    constraint.Part0 = partA
    constraint.Part1 = partB
    constraint.C0 = att0.CFrame
    constraint.C1 = att1.CFrame
    att0:Destroy()
    att1:Destroy()
else
    constraint = Instance.new(cType .. "Constraint")
    constraint.Attachment0 = att0
    constraint.Attachment1 = att1
end

constraint.Name = "Connection_" .. partB.Name
constraint.Parent = partA
pcall(function() constraint.Visible = true end)

return "Successfully connected " .. partA.Name .. " and " .. partB.Name .. " with " .. cType
