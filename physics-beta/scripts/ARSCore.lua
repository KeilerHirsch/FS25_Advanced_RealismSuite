-- Single-player physics-only ARS comparison harness.
ARS = { running=false, mission=nil, settings={physics=true}, available={}, conflicts={} }
local function packResults(...) return {n=select("#",...),...} end
function ARS.callWithRestore(restore, callback, ...)
    local results=packResults(pcall(callback,...))
    restore()
    if not results[1] then error(results[2],0) end
    return unpack(results,2,results.n)
end
function ARS:isEnabled(key)
    return self.running and self.mission==g_currentMission
        and self.settings[key]==true and self.available[key]==true
end
function ARS:loadMap()
    self.mission=g_currentMission
    self.running=true
    if ARSPhysics~=nil then ARSPhysics:installHooks() end
    print("[ARS Physics Beta] native GIANTS friction, sink, rolling and tool resistance enabled")
    if g_server~=nil and type(addConsoleCommand)=="function" then
        addConsoleCommand("arsCurve","ARS Physics: inspect soil curves","consoleCurve",ARSPhysics)
    end
end
function ARS:deleteMap()
    self.running=false
    if ARSPhysics~=nil then ARSPhysics.restore() end
    if type(removeConsoleCommand)=="function" then removeConsoleCommand("arsCurve") end
    self.mission=nil
end
