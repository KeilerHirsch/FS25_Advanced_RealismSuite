-- Regression: FS25 WheelPhysics.serverUpdate performs updateContact before
-- checking extraSinkSupported and calling updateSink. A water transition
-- after ARS prepares the gate must not add native water sinking to wheels
-- whose original XML did not enable extraSinkSupported.
ARS = {available={}, isEnabled=function() return true end}
ARS.callWithRestore = function(cleanup,callback,...)
    local ok,result = pcall(callback,...)
    cleanup()
    assert(ok,result)
    return result
end
Platform = {gameplay={wheelTerrainDisplacement=true}}
FieldGroundType = {NONE=0, PLOWED=1}
WheelContactType = {NONE=0, GROUND=1}
WheelsUtil = {
    GROUND_ROAD=101,
    GROUND_HARD_TERRAIN=102,
    getGroundType=function() return 102 end,
    getTireTypeName=function() return "STREET" end
}
PowerConsumer = {onUpdate=function() end}
local nativeSinkCalls = 0
WheelPhysics = {
    MAX_SINK={[0]=0, [1]=0.1},
    WATER_SINK=0.12,
    updateFriction=function() end,
    updatePhysics=function() end,
    updateSink=function(wp,dt,wet)
        nativeSinkCalls = nativeSinkCalls + 1
    end,
    serverUpdate=function(wp,dt,index,wet)
        -- Mirrors the FS25 order: updateContact precedes the sink gate.
        if type(wp.updateContact) == "function" then wp:updateContact() end
        if wp.extraSinkSupported then WheelPhysics.updateSink(wp,dt,wet) end
    end
}
dofile("physics-beta/scripts/ARSPhysics.lua")
ARSPhysics:installHooks()

local function wheel(supported, water, updateContact)
    local vehicle = {isServer=true, isAddedToPhysics=true}
    local wp = {
        vehicle=vehicle,
        densityType=FieldGroundType.PLOWED,
        contact=WheelContactType.GROUND,
        hasWaterContact=water,
        extraSinkSupported=supported,
        extraSinkMaxValue=0.20,
        supportsWheelSink=true,
        radius=1,
        sink=0.10,
        sinkTarget=0.10,
        deltaYOriginal=0.05,
        deltaY=0.15,
        updateContact=updateContact
    }
    return wp
end

-- Water already known before ARS prepares the gate: the unsupported wheel
-- remains outside GIANTS updateSink and its saved native cap is restored.
local knownWater = wheel(false, true, function(self) self.hasWaterContact=true end)
local before = nativeSinkCalls
WheelPhysics.serverUpdate(knownWater,100,1,0)
assert(nativeSinkCalls == before, "Known water contact must not call native sink for a disabled wheel")
assert(knownWater.extraSinkSupported == false, "Known water must keep the original disabled gate")
assert(knownWater.extraSinkMaxValue == 0.20, "Known water must restore the original sink cap")

-- Water arrives in updateContact after ARS prepared the dry-soil gate. The
-- updateSink wrapper must stop the just-enabled native call for this wheel.
local transition = wheel(false, false, function(self) self.hasWaterContact=true end)
before = nativeSinkCalls
WheelPhysics.serverUpdate(transition,100,1,0)
assert(nativeSinkCalls == before, "Water transition must not invoke native sink for an originally disabled wheel")
assert(transition.extraSinkSupported == false, "Water transition must close the temporary native gate")
assert(transition.extraSinkMaxValue == 0.20, "Water transition must restore the original sink cap")
assert(transition.sink < 0.10 and transition.sink > 0,
    "Water transition must relax existing ARS sink progressively")
assert(math.abs(transition.deltaY-transition.deltaYOriginal-transition.sink)<0.000001,
    "Water transition must keep wheel deltaY aligned with sink")

-- Wheels that natively supported extra sinking retain GIANTS' water path.
local nativeWheel = wheel(true, false, function(self) self.hasWaterContact=true end)
before = nativeSinkCalls
WheelPhysics.serverUpdate(nativeWheel,100,1,0)
assert(nativeSinkCalls == before + 1, "Originally enabled native water sink must remain available")
assert(nativeWheel.extraSinkSupported == true, "Native water wheel support must be preserved")
assert(nativeWheel.extraSinkMaxValue == 0.20, "Native water wheel cap must be preserved")

-- On leaving water, the unsupported wheel is not re-enabled mid-update. It
-- becomes eligible on the next dry update and then uses the ARS path again.
local leaving = wheel(false, true, function(self) self.hasWaterContact=false end)
before = nativeSinkCalls
WheelPhysics.serverUpdate(leaving,100,1,0)
assert(nativeSinkCalls == before, "Water exit tick must remain closed until the next dry update")
assert(leaving.extraSinkSupported == false, "Water exit tick must retain the original disabled gate")
WheelPhysics.serverUpdate(leaving,100,1,0)
assert(nativeSinkCalls == before + 1, "Dry update after water exit should restore the ARS sink path")
assert(leaving.extraSinkSupported == true, "Dry native terrain should re-enable ARS sinking")

ARSPhysics.restore()
print("PASS: water gate preserves originally unsupported wheels and native water behavior")
