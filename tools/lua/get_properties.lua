local target = {path}
if not target then print("Error: Object not found.") return end

local function serialize(val)
    if type(val) == "userdata" then
        return tostring(val)
    end
    return val
end

print("--- Properties for: " .. target:GetFullName() .. " ---")
-- Exhaustive property lists for major classes to prevent "blindness"
local classProps = {
    Lighting = {"Ambient", "Brightness", "ColorShift_Bottom", "ColorShift_Top", "OutdoorAmbient", "ClockTime", "GeographicLatitude", "EnvironmentDiffuseScale", "EnvironmentSpecularScale", "ExposureCompensation", "FogColor", "FogEnd", "FogStart", "GlobalShadows", "ShadowSoftness"},
    Atmosphere = {"Color", "Decay", "Density", "Glare", "Haze", "Offset"},
    BloomEffect = {"Intensity", "Size", "Threshold"},
    ColorCorrectionEffect = {"Brightness", "Contrast", "Saturation", "TintColor"},
    SunRaysEffect = {"Intensity", "Spread"},
    Sky = {"SkyboxBk", "SkyboxDn", "SkyboxFt", "SkyboxLf", "SkyboxRt", "SkyboxUp", "SunAngularSize", "MoonAngularSize", "StarCount"},
    Humanoid = {"Health", "MaxHealth", "WalkSpeed", "JumpPower", "HipHeight", "MoveDirection", "AutoRotate", "Sit", "PlatformStand", "Jump", "TargetPoint"},
    BasePart = {"Anchored", "CanCollide", "CanTouch", "CanQuery", "Mass", "Position", "Size", "CFrame", "Transparency", "Color", "Material", "Reflectance", "Velocity", "RotVelocity", "AssemblyLinearVelocity", "AssemblyAngularVelocity"},
    Model = {"PrimaryPart", "WorldPivot"},
    SpawnLocation = {"AllowTeamChangeOnTouch", "Duration", "Enabled", "Neutral", "TeamColor"},
    ParticleEmitter = {"Color", "Size", "Texture", "Transparency", "ZOffset", "Lifetime", "Rate", "Rotation", "RotSpeed", "Speed", "SpreadAngle", "Enabled"},
    PointLight = {"Brightness", "Color", "Range", "Shadows", "Enabled"},
    SpotLight = {"Angle", "Brightness", "Color", "Range", "Shadows", "Enabled"},
    SurfaceLight = {"Angle", "Brightness", "Color", "Range", "Shadows", "Enabled"},
    Sound = {"SoundId", "Volume", "PlaybackSpeed", "Playing", "Looped", "TimePosition"},
    DataModel = {"PlaceId", "GameId", "JobId"},
    Terrain = {"Decoration", "GrassLength", "WaterColor", "WaterTransparency", "WaterWaveSize", "WaterWaveSpeed"},
    GuiObject = {"Size", "Position", "BackgroundColor3", "BackgroundTransparency", "Visible", "ZIndex", "LayoutOrder", "AnchorPoint"},
    TextLabel = {"Text", "TextColor3", "TextSize", "Font", "TextTransparency", "TextStrokeTransparency", "TextXAlignment", "TextYAlignment"},
    TextButton = {"Text", "TextColor3", "TextSize", "Font", "AutoButtonColor"},
    ImageLabel = {"Image", "ImageColor3", "ImageTransparency", "ScaleType", "TileSize"},
    ScrollingFrame = {"CanvasSize", "CanvasPosition", "ScrollBarThickness", "ScrollBarImageColor3"},
    UIListLayout = {"Padding", "FillDirection", "HorizontalAlignment", "VerticalAlignment", "SortOrder"},
    UIGridLayout = {"CellSize", "CellPadding", "FillDirection", "FillDirectionMaxCells"}
}

local toCheck = {"Name", "ClassName", "Parent"}

-- Add properties based on class and inheritance
for className, props in pairs(classProps) do
    if target:IsA(className) then
        for _, p in ipairs(props) do table.insert(toCheck, p) end
    end
end

-- Deduplicate and sort
local unique = {}
local final = {}
for _, p in ipairs(toCheck) do
    if not unique[p] then
        unique[p] = true
        table.insert(final, p)
    end
end

for _, prop in ipairs(final) do
    local s, v = pcall(function() return target[prop] end)
    if s then
        print(prop .. ": " .. tostring(serialize(v)))
    end
end

