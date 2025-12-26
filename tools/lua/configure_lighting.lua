local lighting = game:GetService("Lighting")
local preset = args.preset or "RealisticDay"

for _, child in ipairs(lighting:GetChildren()) do
    if child:IsA("PostEffect") or child:IsA("Atmosphere") or child:IsA("Sky") or child:IsA("SunRaysEffect") then
        child:Destroy()
    end
end

local presets = {
    RealisticDay = {
        Ambient = Color3.fromRGB(120, 120, 120),
        OutdoorAmbient = Color3.fromRGB(130, 130, 130),
        Brightness = 2.5,
        TimeOfDay = "14:00:00",
        ShadowSoftness = 0.1,
        EnvironmentDiffuseScale = 1,
        EnvironmentSpecularScale = 1,
        Atmosphere = {Density = 0.2, Offset = 0, Color = Color3.fromRGB(190, 210, 230), Decay = Color3.fromRGB(100, 120, 140), Glare = 0.2, Haze = 0.1},
        Sky = {
            SunAngularSize = 10,
            StarCount = 0,
            SkyboxBk = "rbxassetid://1510166687",
            SkyboxDn = "rbxassetid://1510166687",
            SkyboxFt = "rbxassetid://1510166687",
            SkyboxLf = "rbxassetid://1510166687",
            SkyboxRt = "rbxassetid://1510166687",
            SkyboxUp = "rbxassetid://1510166687"
        },
        SunRays = {Intensity = 0.05, Spread = 0.1},
        Bloom = {Intensity = 0.5, Size = 12, Threshold = 1.5}
    },
    CinematicNight = {
        Ambient = Color3.fromRGB(30, 30, 45),
        OutdoorAmbient = Color3.fromRGB(20, 20, 40),
        Brightness = 0.5,
        TimeOfDay = "00:00:00",
        ShadowSoftness = 0.8,
        EnvironmentDiffuseScale = 0.3,
        EnvironmentSpecularScale = 0.3,
        ExposureCompensation = 0.1,
        Atmosphere = {Density = 0.3, Offset = 0, Color = Color3.fromRGB(20, 20, 50), Decay = Color3.fromRGB(0, 0, 10), Glare = 0, Haze = 0},
        Sky = {
            SunAngularSize = 0,
            StarCount = 3000,
            SkyboxBk = "rbxassetid://217983655",
            SkyboxDn = "rbxassetid://217983655",
            SkyboxFt = "rbxassetid://217983655",
            SkyboxLf = "rbxassetid://217983655",
            SkyboxRt = "rbxassetid://217983655",
            SkyboxUp = "rbxassetid://217983655"
        },
        ColorCorrection = {Brightness = 0, Contrast = 0.1, Saturation = -0.1, TintColor = Color3.fromRGB(200, 220, 255)},
        Bloom = {Intensity = 2, Size = 24, Threshold = 0.5}
    },
    DreamySunset = {
        Ambient = Color3.fromRGB(90, 75, 70),
        OutdoorAmbient = Color3.fromRGB(110, 90, 80),
        Brightness = 2.5,
        TimeOfDay = "17:15:00",
        ShadowSoftness = 0.4,
        EnvironmentDiffuseScale = 0.8,
        EnvironmentSpecularScale = 0.8,
        Atmosphere = {Density = 0.25, Offset = 0, Color = Color3.fromRGB(255, 190, 150), Decay = Color3.fromRGB(100, 50, 25), Glare = 0.6, Haze = 0.3},
        Sky = {
            SunAngularSize = 11,
            StarCount = 0,
            SkyboxBk = "rbxassetid://1510166687",
            SkyboxDn = "rbxassetid://1510166687",
            SkyboxFt = "rbxassetid://1510166687",
            SkyboxLf = "rbxassetid://1510166687",
            SkyboxRt = "rbxassetid://1510166687",
            SkyboxUp = "rbxassetid://1510166687"
        },
        SunRays = {Intensity = 0.15, Spread = 0.2},
        ColorCorrection = {Brightness = 0.02, Contrast = 0.1, Saturation = 0.1, TintColor = Color3.fromRGB(255, 240, 230)}
    },
    Horror = {
        Ambient = Color3.fromRGB(40, 45, 50),
        OutdoorAmbient = Color3.fromRGB(20, 25, 30),
        Brightness = 0.8,
        TimeOfDay = "02:00:00",
        ShadowSoftness = 1,
        EnvironmentDiffuseScale = 0.2,
        EnvironmentSpecularScale = 0.2,
        ExposureCompensation = -0.2,
        Atmosphere = {Density = 0.5, Offset = 0, Color = Color3.fromRGB(20, 25, 20), Decay = Color3.fromRGB(5, 10, 5), Glare = 0, Haze = 2.0},
        Sky = {
            SunAngularSize = 0,
            MoonAngularSize = 0,
            StarCount = 500,
            SkyboxBk = "rbxassetid://149397635",
            SkyboxDn = "rbxassetid://149397635",
            SkyboxFt = "rbxassetid://149397635",
            SkyboxLf = "rbxassetid://149397635",
            SkyboxRt = "rbxassetid://149397635",
            SkyboxUp = "rbxassetid://149397635"
        },
        ColorCorrection = {Brightness = -0.05, Contrast = 0.3, Saturation = -0.5, TintColor = Color3.fromRGB(180, 200, 210)},
        Bloom = {Intensity = 1.0, Size = 24, Threshold = 0.9}
    },
    NeutralStudio = {
        Ambient = Color3.fromRGB(127, 127, 127),
        OutdoorAmbient = Color3.fromRGB(127, 127, 127),
        Brightness = 2,
        TimeOfDay = "12:00:00",
        ShadowSoftness = 0,
        EnvironmentDiffuseScale = 1,
        EnvironmentSpecularScale = 1,
        Atmosphere = {Density = 0, Offset = 0, Color = Color3.fromRGB(255, 255, 255), Decay = Color3.fromRGB(255, 255, 255), Glare = 0, Haze = 0},
        Sky = {
            SunAngularSize = 11,
            StarCount = 0,
            SkyboxBk = "rbxassetid://1510166687",
            SkyboxDn = "rbxassetid://1510166687",
            SkyboxFt = "rbxassetid://1510166687",
            SkyboxLf = "rbxassetid://1510166687",
            SkyboxRt = "rbxassetid://1510166687",
            SkyboxUp = "rbxassetid://1510166687"
        }
    }
}

local p = presets[preset] or presets.RealisticDay

lighting.Ambient = p.Ambient
lighting.OutdoorAmbient = p.OutdoorAmbient
lighting.Brightness = p.Brightness
lighting.TimeOfDay = p.TimeOfDay
lighting.ShadowSoftness = p.ShadowSoftness
lighting.EnvironmentDiffuseScale = p.EnvironmentDiffuseScale or 0
lighting.EnvironmentSpecularScale = p.EnvironmentSpecularScale or 0
lighting.GlobalShadows = true
if p.ExposureCompensation then lighting.ExposureCompensation = p.ExposureCompensation end

local atmos = Instance.new("Atmosphere")
atmos.Density = p.Atmosphere.Density
atmos.Offset = p.Atmosphere.Offset
atmos.Color = p.Atmosphere.Color
atmos.Decay = p.Atmosphere.Decay
atmos.Glare = p.Atmosphere.Glare or 0
atmos.Haze = p.Atmosphere.Haze or 0
atmos.Parent = lighting

if p.Sky then
    local sky = Instance.new("Sky")
    for prop, value in pairs(p.Sky) do sky[prop] = value end
    sky.Parent = lighting
end

if p.ColorCorrection then
    local cc = Instance.new("ColorCorrectionEffect")
    cc.Brightness = p.ColorCorrection.Brightness or 0
    cc.Contrast = p.ColorCorrection.Contrast or 0
    cc.Saturation = p.ColorCorrection.Saturation or 0
    cc.TintColor = p.ColorCorrection.TintColor or Color3.fromRGB(255, 255, 255)
    cc.Parent = lighting
end

if p.Bloom then
    local bloom = Instance.new("BloomEffect")
    bloom.Intensity = p.Bloom.Intensity or 1
    bloom.Size = p.Bloom.Size or 24
    bloom.Threshold = p.Bloom.Threshold or 2
    bloom.Parent = lighting
end

if p.SunRays then
    local sun = Instance.new("SunRaysEffect")
    sun.Intensity = p.SunRays.Intensity or 0.1
    sun.Spread = p.SunRays.Spread or 0.1
    sun.Parent = lighting
end

return "Applied lighting preset: " .. preset
