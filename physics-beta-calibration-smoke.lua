ARS = {available={},isEnabled=function() return true end}
g_server = {}
WheelPhysics = {updateFriction=function() end, updateSink=function() end, updatePhysics=function() end}
PowerConsumer = {onUpdate=function() end}
local motorFn = function() return {42},{1} end
VehicleMotor = {getTorqueAndSpeedValues=motorFn}
dofile("physics-beta/scripts/ARSPhysics.lua")
assert(ARSPhysics.VERSION=="0.1.18.9")
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
print("PASS: Physics 0.1.18.9 profile smoke and untouched native torque")