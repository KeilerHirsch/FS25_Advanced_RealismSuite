ARS = {available={},isEnabled=function() return true end}
g_server = {}
WheelPhysics = {updateFriction=function() end, updateSink=function() end, updatePhysics=function() end}
PowerConsumer = {onUpdate=function() end}
local motorFn = function() return {42},{1} end
VehicleMotor = {getTorqueAndSpeedValues=motorFn}
dofile("physics-beta/scripts/ARSPhysics.lua")
assert(ARSPhysics.VERSION=="0.1.18.10")
for _,entry in ipairs({
    {"road",1.00,1.00,1.00,1.00},
    {"field",1.030,1.095,1.035,1.00},
    {"cultivated",1.045,1.160,1.055,1.025},
    {"plowed",1.020,1.200,1.080,1.055},
    {"seedbed",1.045,1.145,1.045,1.015},
    {"soft",0.975,1.220,1.095,1.045}
}) do
   local actual = ARSPhysics:consoleCurve(entry[1])
   for i=2,5 do assert(actual:find(string.format("%.3f",entry[i]),1,true),entry[1]..":"..actual) end
end
ARSPhysics:installHooks()
assert(VehicleMotor.getTorqueAndSpeedValues==motorFn,"Native motor torque hook unexpectedly changed")
assert(ARSPhysics.drivetrainHookInstalled~=true,"Unexpected motor hook")
local seen = {}
WheelPhysics.updatePhysics = function(wp)
    seen[#seen+1] = wp.rotationDamping
end
ARS.callWithRestore = function(cleanup,fn,...)
    local value = fn(...)
    cleanup()
    return value
end
-- Reinstall wrappers with our observed vanilla mock.
ARSPhysics.hooksInstalled = false
ARSPhysics:installHooks()
local function makeWheel(isTrailer)
    local v = {isServer=true, isAddedToPhysics=true,
        spec_wheels={wheels={{},{},{},{}}}, getTotalMass=function() return 20 end}
    if isTrailer then v.spec_trailer={} end
    return {vehicle=v, rotationDamping=1, densityType=1, wheelShapeWidth=0.6}
end
FieldGroundType = {NONE=0,CULTIVATED=1}
local trailer = makeWheel(true)
local tractor = makeWheel(false)
WheelPhysics.updatePhysics(trailer,0,0)
WheelPhysics.updatePhysics(tractor,0,0)
assert(math.abs(seen[1]-seen[2])<0.000001,"Unintended trailer flat rolling tax")
assert(trailer.rotationDamping==1 and tractor.rotationDamping==1,"Damping not restored")
assert(seen[1]>1.05 and seen[1]<1.15,"Soil rolling no longer works")
-- Every wheeled vehicle, including all trailer/implement classes, uses
-- the existing per-wheel load. Wetness only adds a small road rolling term.
local measured = {}
WheelPhysics.updatePhysics = function(wp)
    measured[#measured+1] = wp.rotationDamping
end
WheelsUtil = {
    GROUND_ROAD=101,
    GROUND_HARD_TERRAIN=102,
    getGroundType=function(isField) return 101 end,
    getTireTypeName=function() return "STREET" end
}
WheelContactType={GROUND=1}
FieldGroundType={NONE=0,CULTIVATED=1}
local groundWet=0
g_currentMission={environment={weather={getGroundWetness=function() return groundWet end}}}
ARSPhysics.hooksInstalled=false
ARSPhysics:installHooks()
assert(VehicleMotor.getTorqueAndSpeedValues==motorFn,"Native torque was altered")
local function onRoad(mass,wet,kind)
    local v={isServer=true,isAddedToPhysics=true,spec_wheels={wheels={{},{},{},{}}},
        getTotalMass=function(self,onlyGiven) assert(onlyGiven==true); return mass end}
    if kind=="trailer" then v.spec_trailer={} end
    if kind=="implement" then v.spec_fillUnit={} end
    if kind=="tractor" then v.spec_motorized={} end
    groundWet=wet
    local wp={vehicle=v,densityType=0,contact=1,rotationDamping=1,
        wheelShapeWidth=0.6,groundDepth=0}
    WheelPhysics.updatePhysics(wp,0,0)
    assert(wp.rotationDamping==1,"Road rolling damping not restored")
    return measured[#measured]
end
local light=onRoad(6,0,"tractor")
local full=onRoad(24,0,"tractor")
local trailer=onRoad(24,0,"trailer")
local implement=onRoad(24,0,"implement")
local wet=onRoad(24,1,"trailer")
assert(light>=1 and light<1.001,"Light road vehicle not near vanilla")
assert(full>light and full<=1.01201,"Road load effect should be <=1.2%")
assert(math.abs(full-trailer)<0.000001,"Unexpected trailer-class bias")
assert(math.abs(full-implement)<0.000001,"Unsupported implement-class bias")
assert(wet>trailer and wet<=1.01601,"Wetness road effect out of bounds")
assert(math.abs(wet-trailer-0.004)<0.000001,"Wetness factor unexpected")
print("PASS: road/hard load, trailer, fill mass, wetness and cap")
print("PASS: Physics 0.1.18.10 profile smoke and untouched native torque")