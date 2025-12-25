local stats = game:GetService("Stats")
print("--- Studio Performance Stats ---")
print("Memory Usage: " .. string.format("%.2f", stats:GetTotalMemoryUsageMb()) .. " MB")
print("Instance Count: " .. stats.InstanceCount)
print("Draw Calls: " .. stats.PrimitivesRendered)
print("Physics FPS: " .. string.format("%.2f", stats.PhysicsFps))

