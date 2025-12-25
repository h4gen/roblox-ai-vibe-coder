local preset = "{preset}" -- "RealisticDay", "CinematicNight", "DreamySunset", "Horror", "NeutralStudio"
local lighting = game:GetService("Lighting")

print("Applying Lighting Preset: " .. preset)

-- 1. Cleanup existing post-effects
for _, child in ipairs(lighting:GetChildren()) do
    if child:IsA("PostEffect") or child:IsA("Sky") or child:IsA("Atmosphere") then
        child:Destroy()
    end
end

-- 2. Define Presets
local presets = {
    RealisticDay = {
        Ambient = Color3.fromRGB(70, 70, 70),
        OutdoorAmbient = Color3.fromRGB(100, 100, 100),
        Brightness = 2,
        TimeOfDay = "14:00:00",
        ShadowSoftness = 0.2,
        EnvironmentDiffuseScale = 1,
        EnvironmentSpecularScale = 1,
        Atmosphere = {Density = 0.3, Offset = 0, Color = Color3.fromRGB(199, 213, 224), Decay = Color3.fromRGB(106, 106, 106), Glare = 0, Haze = 0},
        -- Using a known high-quality skybox asset or default
        SkyId = "rbxassetid://15101662453" 
    },
    CinematicNight = {
        Ambient = Color3.fromRGB(0, 0, 0),
        OutdoorAmbient = Color3.fromRGB(20, 20, 35),
        Brightness = 0,
        TimeOfDay = "00:00:00",
        ShadowSoftness = 0,
        EnvironmentDiffuseScale = 0.2,
        EnvironmentSpecularScale = 0.2,
        Atmosphere = {Density = 0.35, Offset = 0, Color = Color3.fromRGB(40, 40, 60), Decay = Color3.fromRGB(20, 20, 35), Glare = 0, Haze = 0},
        SkyId = "rbxassetid://144933338" 
    },
    DreamySunset = {
        Ambient = Color3.fromRGB(60, 40, 40),
        OutdoorAmbient = Color3.fromRGB(80, 50, 40),
        Brightness = 1,
        TimeOfDay = "17:45:00",
        ShadowSoftness = 0.2,
        EnvironmentDiffuseScale = 0.8,
        EnvironmentSpecularScale = 0.8,
        Atmosphere = {Density = 0.32, Offset = 0, Color = Color3.fromRGB(200, 100, 50), Decay = Color3.fromRGB(100, 50, 50), Glare = 0.5, Haze = 1},
        SkyId = "rbxassetid://217983655"
    },
    Horror = {
        Ambient = Color3.fromRGB(5, 0, 0),
        OutdoorAmbient = Color3.fromRGB(0, 0, 0),
        Brightness = 0,
        TimeOfDay = "00:00:00",
        ShadowSoftness = 1,
        EnvironmentDiffuseScale = 0,
        EnvironmentSpecularScale = 0,
        Atmosphere = {Density = 0.65, Offset = 0, Color = Color3.fromRGB(20, 0, 0), Decay = Color3.fromRGB(0, 0, 0), Glare = 0, Haze = 2},
        FogColor = Color3.fromRGB(10, 0, 0),
        FogEnd = 100,
        SkyId = "rbxassetid://149397635"
    },
    NeutralStudio = {
        Ambient = Color3.fromRGB(200, 200, 200),
        OutdoorAmbient = Color3.fromRGB(150, 150, 150),
        Brightness = 1,
        TimeOfDay = "12:00:00",
        ShadowSoftness = 0.5,
        EnvironmentDiffuseScale = 0.5,
        EnvironmentSpecularScale = 0.5,
        Atmosphere = {Density = 0.1, Offset = 0, Color = Color3.fromRGB(255, 255, 255), Decay = Color3.fromRGB(255, 255, 255), Glare = 0, Haze = 0},
        SkyId = "" 
    }
}

local p = presets[preset] or presets.RealisticDay

-- 3. Apply Core Lighting Props
lighting.Ambient = p.Ambient
lighting.OutdoorAmbient = p.OutdoorAmbient
lighting.Brightness = p.Brightness
lighting.TimeOfDay = p.TimeOfDay
lighting.ShadowSoftness = p.ShadowSoftness
lighting.EnvironmentDiffuseScale = p.EnvironmentDiffuseScale or 0
lighting.EnvironmentSpecularScale = p.EnvironmentSpecularScale or 0
lighting.GlobalShadows = true
if p.FogColor then lighting.FogColor = p.FogColor end
if p.FogEnd then lighting.FogEnd = p.FogEnd end

-- 4. Create Atmosphere
local atmos = Instance.new("Atmosphere")
atmos.Name = "Atmosphere"
atmos.Density = p.Atmosphere.Density
atmos.Offset = p.Atmosphere.Offset
atmos.Color = p.Atmosphere.Color
atmos.Decay = p.Atmosphere.Decay
atmos.Glare = p.Atmosphere.Glare or 0
atmos.Haze = p.Atmosphere.Haze or 0
atmos.Parent = lighting

-- 5. Create Sky
if p.SkyId and p.SkyId ~= "" then
    local sky = Instance.new("Sky")
    sky.Name = "Sky"
    sky.SkyboxBk = p.SkyId
    sky.SkyboxDn = p.SkyId
    sky.SkyboxFt = p.SkyId
    sky.SkyboxLf = p.SkyId
    sky.SkyboxRt = p.SkyId
    sky.SkyboxUp = p.SkyId
    -- Use a generic sun texture
    sky.SunTextureId = "rbxassetid://6196665106"
    sky.Parent = lighting
end

-- 6. Add Post Effects
local bloom = Instance.new("BloomEffect")
bloom.Name = "Bloom"
bloom.Intensity = 0.4
bloom.Size = 24
bloom.Threshold = 2
bloom.Parent = lighting

local colorCor = Instance.new("ColorCorrectionEffect")
colorCor.Name = "ColorCorrection"
if preset == "Horror" then
    colorCor.Saturation = -0.5
    colorCor.Contrast = 0.2
elseif preset == "DreamySunset" then
    colorCor.Saturation = 0.2
    colorCor.TintColor = Color3.fromRGB(255, 240, 230)
else
    colorCor.Saturation = 0.1
    colorCor.Contrast = 0.1
end
colorCor.Parent = lighting

local sunRays = Instance.new("SunRaysEffect")
sunRays.Name = "SunRays"
sunRays.Intensity = 0.1
sunRays.Parent = lighting

return "Applied lighting preset: " .. preset
