local target = {path}
if not target then print("Error: Object not found.") return end

print("--- Info for: " .. target:GetFullName() .. " ---")
print("ClassName: " .. target.ClassName)

if target:IsA("BasePart") then
    print("Size: " .. tostring(target.Size))
    print("Position: " .. tostring(target.Position))
elseif target:IsA("Model") then
    print("ExtentsSize: " .. tostring(target:GetExtentsSize()))
    print("PrimaryPart: " .. tostring(target.PrimaryPart))
end

local atts = target:GetAttributes()
print("Attributes:")
for k, v in pairs(atts) do
    print("  " .. k .. ": " .. tostring(v))
end

local tags = game:GetService("CollectionService"):GetTags(target)
print("Tags: " .. table.concat(tags, ", "))

