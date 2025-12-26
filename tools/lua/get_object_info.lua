local target, err = SafeResolve(args.path)
if not target then return "Error: Object not found. " .. (err or "") end

local res = "--- Info for: " .. target:GetFullName() .. " ---\n"
res = res .. "ClassName: " .. target.ClassName .. "\n"

if target:IsA("BasePart") then
    res = res .. "Size: " .. tostring(target.Size) .. "\n"
    res = res .. "Position: " .. tostring(target.Position) .. "\n"
    res = res .. "Orientation: " .. tostring(target.Orientation) .. "\n"
    res = res .. "Anchored: " .. tostring(target.Anchored) .. "\n"
    res = res .. "CanCollide: " .. tostring(target.CanCollide) .. "\n"
elseif target:IsA("Model") then
    local cf, size = target:GetBoundingBox()
    res = res .. "BoundingBox Center: " .. tostring(cf.Position) .. "\n"
    res = res .. "BoundingBox Size: " .. tostring(size) .. "\n"
    res = res .. "PrimaryPart: " .. (target.PrimaryPart and target.PrimaryPart:GetFullName() or "nil") .. "\n"
end

local atts = target:GetAttributes()
res = res .. "Attributes:\n"
for k, v in pairs(atts) do
    res = res .. "  " .. k .. ": " .. tostring(v) .. "\n"
end

local tags = game:GetService("CollectionService"):GetTags(target)
res = res .. "Tags: " .. table.concat(tags, ", ") .. "\n"

-- List children summary if it has many
local children = target:GetChildren()
if #children > 0 then
    res = res .. "Children Count: " .. #children .. "\n"
    if #children <= 20 then
        res = res .. "Children: "
        local names = {}
        for _, c in ipairs(children) do table.insert(names, c.Name .. " [" .. c.ClassName .. "]") end
        res = res .. table.concat(names, ", ") .. "\n"
    else
        res = res .. "First 20 Children: "
        local names = {}
        for i=1, 20 do table.insert(names, children[i].Name .. " [" .. children[i].ClassName .. "]") end
        res = res .. table.concat(names, ", ") .. " ...\n"
    end
end

return res
