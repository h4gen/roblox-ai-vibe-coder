local stats = game:GetService("Stats")
local res = "--- Studio Performance Stats ---\n"
res = res .. "Memory Usage: " .. string.format("%.2f", stats:GetTotalMemoryUsageMb()) .. " MB\n"
res = res .. "Instance Count: " .. stats.InstanceCount .. "\n"
res = res .. "Draw Calls: " .. stats.PrimitivesRendered .. "\n"
res = res .. "Physics FPS: " .. string.format("%.2f", stats.PhysicsFps) .. "\n"
return res
