local function getDirection(refPart, targetPos)
    local localPos = refPart.CFrame:PointToObjectSpace(targetPos)
    local x, y, z = localPos.X, localPos.Y, localPos.Z
    
    local horizontal = ""
    local vertical = ""
    local depth = ""

    if math.abs(z) > 3 then depth = (z > 0 and "behind" or "in front of") end
    if math.abs(x) > 3 then horizontal = (x > 0 and "to the right" or "to the left") end
    if math.abs(y) > 5 then vertical = (y > 0 and "above" or "below") end

    local result = {}
    if depth ~= "" then table.insert(result, depth) end
    if horizontal ~= "" then table.insert(result, horizontal) end
    if vertical ~= "" then table.insert(result, vertical) end
    
    if #result == 0 then return "right at" end
    return table.concat(result, " and ")
end

-- Use Player's character or SpawnLocation as reference
local ref = workspace:FindFirstChildWhichIsA("SpawnLocation", true)
for _, p in pairs(game.Players:GetPlayers()) do
    if p.Character and p.Character:FindFirstChild("HumanoidRootPart") then
        ref = p.Character.HumanoidRootPart
        break
    end
end

if not ref then 
    print("--- Spatial Summary ---\nNo reference point (Player/Spawn) found.")
    return
end

local summary = string.format("--- Spatial Summary (Relative to %s) ---\n", ref.Name)
local baseplate = workspace:FindFirstChild("Baseplate")
if baseplate then
    summary = summary .. string.format("Baseplate: Size=%s, Pos=%s\n", tostring(baseplate.Size), tostring(baseplate.Position))
end

-- Find major objects and describe them relatively
for _, child in pairs(workspace:GetChildren()) do
    if (child:IsA("Model") and child.PrimaryPart) or (child:IsA("BasePart") and child.Name ~= "Baseplate" and child ~= ref) then
        local pos = child:IsA("Model") and child.PrimaryPart.Position or child.Position
        local dist = (pos - ref.Position).Magnitude
        
        if dist < 200 then -- Focus on things within 200 studs
            local localPos = ref.CFrame:PointToObjectSpace(pos)
            local orientation = child:IsA("Model") and (child.PrimaryPart and child.PrimaryPart.Orientation or Vector3.new(0,0,0)) or child.Orientation
            local dir = getDirection(ref, pos)
            summary = summary .. string.format("- %s: %s (Dist: %.1f, Offset: [%.1f, %.1f, %.1f], Rot: [%.0f, %.1f, %.0f])\n", 
                child.Name, dir, dist, localPos.X, localPos.Y, localPos.Z, orientation.X, orientation.Y, orientation.Z)
        end
    end
end
print(summary)

