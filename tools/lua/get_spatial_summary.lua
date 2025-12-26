local function getDirection(refPart, targetPos)
    local localPos = refPart.CFrame:PointToObjectSpace(targetPos)
    local x, y, z = localPos.X, localPos.Y, localPos.Z
    local result = {}
    if math.abs(z) > 3 then table.insert(result, (z > 0 and "behind" or "in front of")) end
    if math.abs(x) > 3 then table.insert(result, (x > 0 and "to the right" or "to the left")) end
    if math.abs(y) > 5 then table.insert(result, (y > 0 and "above" or "below")) end
    if #result == 0 then return "right at" end
    return table.concat(result, " and ")
end

local ref = workspace:FindFirstChildWhichIsA("SpawnLocation", true)
for _, p in pairs(game.Players:GetPlayers()) do
    if p.Character and p.Character:FindFirstChild("HumanoidRootPart") then
        ref = p.Character.HumanoidRootPart
        break
    end
end

if not ref then return "--- Spatial Summary ---\nNo reference point (Player/Spawn) found." end

local summary = string.format("--- Spatial Summary (Relative to %s at %s) ---\n", ref.Name, tostring(ref.Position))
local baseplate = workspace:FindFirstChild("Baseplate")
if baseplate then
    summary = summary .. string.format("Baseplate: Size=%s, Pos=%s\n", tostring(baseplate.Size), tostring(baseplate.Position))
end

for _, child in pairs(workspace:GetChildren()) do
    if child:IsA("Model") or child:IsA("BasePart") then
        if child.Name == "Baseplate" or child == ref or child == ref.Parent then continue end
        
        local pos, size
        if child:IsA("Model") then
            local cf, s = child:GetBoundingBox()
            pos = cf.Position
            size = s
        else
            pos = child.Position
            size = child.Size
        end
        
        local dist = (pos - ref.Position).Magnitude
        if dist < 300 then -- Increased radius slightly
            local localPos = ref.CFrame:PointToObjectSpace(pos)
            local orientation = child:IsA("Model") and (child.PrimaryPart and child.PrimaryPart.Orientation or Vector3.new(0,0,0)) or child.Orientation
            local dir = getDirection(ref, pos)
            summary = summary .. string.format("- %s [%s]: %s (Dist: %.1f, Size: [%.1f, %.1f, %.1f], Offset: [%.1f, %.1f, %.1f])\n", 
                child.Name, child.ClassName, dir, dist, size.X, size.Y, size.Z, localPos.X, localPos.Y, localPos.Z)
        end
    end
end
return summary
