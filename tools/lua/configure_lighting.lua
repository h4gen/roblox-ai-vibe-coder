local lighting = game:GetService("Lighting")
local preset = "{preset}"

-- 1. Clear ALL existing effects including those added manually by the AI
for _, child in ipairs(lighting:GetChildren()) do
    if child:IsA("PostEffect") or child:IsA("Atmosphere") or child:IsA("Sky") or child:IsA("SunRaysEffect") then
        child:Destroy()
    end
end

-- 2. Define High-Fidelity Presets
local presets = {{
    RealisticDay = {{
        Ambient = Color3.fromRGB(120, 120, 120),
        OutdoorAmbient = Color3.fromRGB(130, 130, 130),
        Brightness = 2.5,
        TimeOfDay = "14:00:00",
        ShadowSoftness = 0.1,
        EnvironmentDiffuseScale = 1,
        EnvironmentSpecularScale = 1,
        Atmosphere = {{Density = 0.2, Offset = 0, Color = Color3.fromRGB(190, 210, 230), Decay = Color3.fromRGB(100, 120, 140), Glare = 0.2, Haze = 0.1}},
        Sky = {{
            SunAngularSize = 10,
            StarCount = 0,
            SkyboxBk = "rbxassetid://1510166687",
            SkyboxDn = "rbxassetid://1510166687",
            SkyboxFt = "rbxassetid://1510166687",
            SkyboxLf = "rbxassetid://1510166687",
            SkyboxRt = "rbxassetid://1510166687",
            SkyboxUp = "rbxassetid://1510166687"
        }},
        SunRays = {{Intensity = 0.05, Spread = 0.1}},
        Bloom = {{Intensity = 0.5, Size = 12, Threshold = 1.5}}
    }},
    CinematicNight = {{
        Ambient = Color3.fromRGB(30, 30, 45),
        OutdoorAmbient = Color3.fromRGB(20, 20, 40),
        Brightness = 0.5,
        TimeOfDay = "00:00:00",
        ShadowSoftness = 0.8,
        EnvironmentDiffuseScale = 0.3,
        EnvironmentSpecularScale = 0.3,
        ExposureCompensation = 0.1,
        Atmosphere = {{Density = 0.3, Offset = 0, Color = Color3.fromRGB(20, 20, 50), Decay = Color3.fromRGB(0, 0, 10), Glare = 0, Haze = 0}},
        Sky = {{
            SunAngularSize = 0,
            StarCount = 3000,
            SkyboxBk = "rbxassetid://217983655",
            SkyboxDn = "rbxassetid://217983655",
            SkyboxFt = "rbxassetid://217983655",
            SkyboxLf = "rbxassetid://217983655",
            SkyboxRt = "rbxassetid://217983655",
            SkyboxUp = "rbxassetid://217983655"
        }},
        ColorCorrection = {{Brightness = 0, Contrast = 0.1, Saturation = -0.1, TintColor = Color3.fromRGB(200, 220, 255)}},
        Bloom = {{Intensity = 2, Size = 24, Threshold = 0.5}}
    }},
    DreamySunset = {{
        Ambient = Color3.fromRGB(90, 75, 70),
        OutdoorAmbient = Color3.fromRGB(110, 90, 80),
        Brightness = 2.5,
        TimeOfDay = "17:15:00",
        ShadowSoftness = 0.4,
        EnvironmentDiffuseScale = 0.8,
        EnvironmentSpecularScale = 0.8,
        Atmosphere = {{Density = 0.25, Offset = 0, Color = Color3.fromRGB(255, 190, 150), Decay = Color3.fromRGB(100, 50, 25), Glare = 0.6, Haze = 0.3}},
        Sky = {{
            SunAngularSize = 11,
            StarCount = 0,
            SkyboxBk = "rbxassetid://1510166687",
            SkyboxDn = "rbxassetid://1510166687",
            SkyboxFt = "rbxassetid://1510166687",
            SkyboxLf = "rbxassetid://1510166687",
            SkyboxRt = "rbxassetid://1510166687",
            SkyboxUp = "rbxassetid://1510166687"
        }},
        SunRays = {{Intensity = 0.15, Spread = 0.2}},
        ColorCorrection = {{Brightness = 0.02, Contrast = 0.1, Saturation = 0.1, TintColor = Color3.fromRGB(255, 240, 230)}}
    }},
    Horror = {{
        Ambient = Color3.fromRGB(40, 45, 50),
        OutdoorAmbient = Color3.fromRGB(20, 25, 30),
        Brightness = 0.8,
        TimeOfDay = "02:00:00",
        ShadowSoftness = 1,
        EnvironmentDiffuseScale = 0.2,
        EnvironmentSpecularScale = 0.2,
        ExposureCompensation = -0.2,
        Atmosphere = {{Density = 0.5, Offset = 0, Color = Color3.fromRGB(20, 25, 20), Decay = Color3.fromRGB(5, 10, 5), Glare = 0, Haze = 2.0}},
        Sky = {{
            SunAngularSize = 0,
            MoonAngularSize = 0,
            StarCount = 500,
            SkyboxBk = "rbxassetid://149397635",
            SkyboxDn = "rbxassetid://149397635",
            SkyboxFt = "rbxassetid://149397635",
            SkyboxLf = "rbxassetid://149397635",
            SkyboxRt = "rbxassetid://149397635",
            SkyboxUp = "rbxassetid://149397635"
        }},
        ColorCorrection = {{Brightness = -0.05, Contrast = 0.3, Saturation = -0.5, TintColor = Color3.fromRGB(180, 200, 210)}},
        Bloom = {{Intensity = 1.0, Size = 24, Threshold = 0.9}}
    }},
    NeutralStudio = {{
        Ambient = Color3.fromRGB(127, 127, 127),
        OutdoorAmbient = Color3.fromRGB(127, 127, 127),
        Brightness = 2,
        TimeOfDay = "12:00:00",
        ShadowSoftness = 0,
        EnvironmentDiffuseScale = 1,
        EnvironmentSpecularScale = 1,
        Atmosphere = {{Density = 0, Offset = 0, Color = Color3.fromRGB(255, 255, 255), Decay = Color3.fromRGB(255, 255, 255), Glare = 0, Haze = 0}},
        Sky = {{
            SunAngularSize = 11,
            StarCount = 0,
            SkyboxBk = "rbxassetid://1510166687",
            SkyboxDn = "rbxassetid://1510166687",
            SkyboxFt = "rbxassetid://1510166687",
            SkyboxLf = "rbxassetid://1510166687",
            SkyboxRt = "rbxassetid://1510166687",
            SkyboxUp = "rbxassetid://1510166687"
        }}
    }},
    CyberpunkNeon = {{
        Ambient = Color3.fromRGB(20, 15, 40),
        OutdoorAmbient = Color3.fromRGB(10, 5, 30),
        Brightness = 0.5,
        TimeOfDay = "22:00:00",
        ShadowSoftness = 0.8,
        EnvironmentDiffuseScale = 0.5,
        EnvironmentSpecularScale = 1,
        ExposureCompensation = 0.5,
        Atmosphere = {{Density = 0.3, Offset = 0, Color = Color3.fromRGB(15, 10, 30), Decay = Color3.fromRGB(80, 0, 150), Glare = 0.1, Haze = 0.5}},
        Sky = {{
            SunAngularSize = 0,
            StarCount = 1000,
            SkyboxBk = "rbxassetid://217983655",
            SkyboxDn = "rbxassetid://217983655",
            SkyboxFt = "rbxassetid://217983655",
            SkyboxLf = "rbxassetid://217983655",
            SkyboxRt = "rbxassetid://217983655",
            SkyboxUp = "rbxassetid://217983655"
        }},
        ColorCorrection = {{Brightness = 0, Contrast = 0.2, Saturation = 0.3, TintColor = Color3.fromRGB(255, 230, 255)}},
        Bloom = {{Intensity = 3, Size = 48, Threshold = 0.3}}
    }},
    TropicalNoon = {{
        Ambient = Color3.fromRGB(150, 160, 170),
        OutdoorAmbient = Color3.fromRGB(180, 190, 200),
        Brightness = 3.5,
        TimeOfDay = "12:30:00",
        ShadowSoftness = 0.05,
        EnvironmentDiffuseScale = 1,
        EnvironmentSpecularScale = 1,
        Atmosphere = {{Density = 0.1, Offset = 0, Color = Color3.fromRGB(200, 230, 255), Decay = Color3.fromRGB(150, 200, 255), Glare = 0.5, Haze = 0}},
        Sky = {{
            SunAngularSize = 21,
            StarCount = 0,
            SkyboxBk = "rbxassetid://1510166687",
            SkyboxDn = "rbxassetid://1510166687",
            SkyboxFt = "rbxassetid://1510166687",
            SkyboxLf = "rbxassetid://1510166687",
            SkyboxRt = "rbxassetid://1510166687",
            SkyboxUp = "rbxassetid://1510166687"
        }},
        ColorCorrection = {{Brightness = 0.05, Contrast = 0.1, Saturation = 0.4, TintColor = Color3.fromRGB(255, 255, 240)}},
        SunRays = {{Intensity = 0.1, Spread = 0.5}}
    }},
    Vaporwave = {{
        Ambient = Color3.fromRGB(150, 100, 150),
        OutdoorAmbient = Color3.fromRGB(100, 70, 130),
        Brightness = 2,
        TimeOfDay = "18:30:00",
        ShadowSoftness = 0.5,
        EnvironmentDiffuseScale = 0.8,
        EnvironmentSpecularScale = 1,
        Atmosphere = {{Density = 0.4, Offset = 0, Color = Color3.fromRGB(255, 100, 200), Decay = Color3.fromRGB(100, 200, 255), Glare = 1.0, Haze = 1.0}},
        Sky = {{
            SunAngularSize = 35,
            StarCount = 500,
            SkyboxBk = "rbxassetid://1510166687",
            SkyboxDn = "rbxassetid://1510166687",
            SkyboxFt = "rbxassetid://1510166687",
            SkyboxLf = "rbxassetid://1510166687",
            SkyboxRt = "rbxassetid://1510166687",
            SkyboxUp = "rbxassetid://1510166687"
        }},
        ColorCorrection = {{Brightness = 0.05, Contrast = 0.2, Saturation = 0.6, TintColor = Color3.fromRGB(255, 200, 255)}},
        Bloom = {{Intensity = 2, Size = 32, Threshold = 0.5}}
    }},
    NordicWinter = {{
        Ambient = Color3.fromRGB(100, 110, 140),
        OutdoorAmbient = Color3.fromRGB(80, 90, 120),
        Brightness = 1.2,
        TimeOfDay = "10:00:00",
        ShadowSoftness = 0.3,
        EnvironmentDiffuseScale = 0.6,
        EnvironmentSpecularScale = 0.6,
        Atmosphere = {{Density = 0.45, Offset = 0, Color = Color3.fromRGB(200, 220, 255), Decay = Color3.fromRGB(150, 160, 200), Glare = 0.1, Haze = 0.5}},
        Sky = {{
            SunAngularSize = 5,
            StarCount = 0,
            SkyboxBk = "rbxassetid://1510166687",
            SkyboxDn = "rbxassetid://1510166687",
            SkyboxFt = "rbxassetid://1510166687",
            SkyboxLf = "rbxassetid://1510166687",
            SkyboxRt = "rbxassetid://1510166687",
            SkyboxUp = "rbxassetid://1510166687"
        }},
        ColorCorrection = {{Brightness = 0, Contrast = 0.1, Saturation = -0.3, TintColor = Color3.fromRGB(220, 240, 255)}}
    }},
    PostApocalyptic = {{
        Ambient = Color3.fromRGB(80, 75, 70),
        OutdoorAmbient = Color3.fromRGB(60, 55, 50),
        Brightness = 1.0,
        TimeOfDay = "16:00:00",
        ShadowSoftness = 0.6,
        EnvironmentDiffuseScale = 0.4,
        EnvironmentSpecularScale = 0.4,
        ExposureCompensation = -0.1,
        Atmosphere = {{Density = 0.6, Offset = 0.5, Color = Color3.fromRGB(150, 130, 110), Decay = Color3.fromRGB(80, 70, 60), Glare = 0, Haze = 3.0}},
        Sky = {{
            SunAngularSize = 0,
            StarCount = 0,
            SkyboxBk = "rbxassetid://149397635",
            SkyboxDn = "rbxassetid://149397635",
            SkyboxFt = "rbxassetid://149397635",
            SkyboxLf = "rbxassetid://149397635",
            SkyboxRt = "rbxassetid://149397635",
            SkyboxUp = "rbxassetid://149397635"
        }},
        ColorCorrection = {{Brightness = -0.05, Contrast = 0.1, Saturation = -0.6, TintColor = Color3.fromRGB(210, 200, 180)}}
    }}
}}

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
if p.ExposureCompensation then lighting.ExposureCompensation = p.ExposureCompensation end
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
if p.Sky then
    local sky = Instance.new("Sky")
    for prop, value in pairs(p.Sky) do
        sky[prop] = value
    end
    sky.Parent = lighting
elseif p.SkyId and p.SkyId ~= "" then
    local sky = Instance.new("Sky")
    sky.SkyboxBk = p.SkyId
    sky.SkyboxDn = p.SkyId
    sky.SkyboxFt = p.SkyId
    sky.SkyboxLf = p.SkyId
    sky.SkyboxRt = p.SkyId
    sky.SkyboxUp = p.SkyId
    sky.Parent = lighting
end

-- 6. Post Processing
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
