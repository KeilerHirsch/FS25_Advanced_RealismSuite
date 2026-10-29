ARS = {available={},isEnabled=function() return true end}
g_server = {}
WheelPhysics = {updateFriction=function() end, updateSink=function() end, updatePhysics=function() end}
PowerConsumer = {onUpdate=function() end}
local motorFn = function() return {42},{1} end
VehicleMotor = {getTorqueAndSpeedValues=motorFn}
dofile("physics-beta/scripts/ARSPhysics.lua")
assert(ARSPhysics.VERSION=="0.1.18.11")
for _,entry in ipairs({
    {"road",1.00,1.00,1.00,1.00},
    {"field",1.030,1.095,1.035,1.00},
    {"cultivated",1.045,1.160,1.055,1.025},
    {"plowed",1.020,1.200,1.080,1.055},
    {"seedbed",1.045,1.145,1.045,1.015},
    {"soft",0.975,1.220,1.095,1.045},
    {"snow",1.00,1.045,1.00,1.00}
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
-- More visible deformation across all compressible surfaces; preserve
-- no artificial sink on paved/hard ground, and preserve the vanilla target.
local sinkSeen = {}
WheelPhysics.MAX_SINK={[0]=0.1,[1]=0.1,[2]=0.1,[3]=0.1,[4]=0.1,[5]=0.1,[6]=0.1}
WheelPhysics.updateSink = function(wp,dt,wet)
    sinkSeen[#sinkSeen+1]=WheelPhysics.MAX_SINK[wp.densityType]
end
FieldGroundType = {
    NONE=0,CULTIVATED=1,PLOWED=2,SEEDBED=3,GRASS=4,
    RIDGE=5,HARVEST_READY=6
}
WheelsUtil.getTireTypeName=function(tireType)
    if tireType==2 then return "CRAWLER" end
    return "STREET"
end
ARSPhysics.hooksInstalled=false
ARSPhysics:installHooks()
local function measureSink(density, mass, wet, crawler, snowy)
    local v={isServer=true,isAddedToPhysics=true,
        spec_wheels={wheels={{},{},{},{}}},
        getTotalMass=function() return mass end}
    local wp={vehicle=v,densityType=density,hasSnowContact=snowy,
        wheelShapeWidth=0.6,tireType=crawler and 2 or 1}
    local original=WheelPhysics.MAX_SINK[density]
    WheelPhysics.updateSink(wp,16,wet)
    assert(WheelPhysics.MAX_SINK[density]==original,"GIANTS global sink constant not restored")
    return sinkSeen[#sinkSeen] / original
end
local normal=measureSink(1,10,0,false,false)
local heavy=measureSink(1,30,0,false,false)
local wet=measureSink(1,10,1,false,false)
local crawled=measureSink(1,10,0,true,false)
assert(normal>1.5 and normal<=2.90,"Soil sink not boosted")
assert(heavy>normal,"Extra load should produce extra sink")
assert(wet>normal,"Wet soil should produce extra sink")
assert(crawled<normal,"Crawler distribution should reduce sink")
assert(measureSink(2,10,0,false,false)>normal,"Plowed must sink more than cultivated")
assert(measureSink(4,10,0,false,false)>1,"Firm field sink boost missing")
assert(measureSink(1,10,0,false,true)>1,"Snow surface sink boost missing")
assert(measureSink(0,10,0,false,false)==1,"Road should not artificially sink")
print("PASS: global deformable ground sink, load, wetness, crawler, snow, road guard, restoration")
print("PASS: Physics 0.1.18.11 profile smoke and untouched native torque")