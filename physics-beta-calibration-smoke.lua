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
    {"soft",0.975,1.220,1.095,1.045},
    {"snow",1.00,1.060,1.00,1.00}
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
assert(math.abs(wet-trailer-0.003)<0.000001,"Wetness factor unexpected")
print("PASS: road/hard load, trailer, fill mass, wetness and cap")
-- More visible deformation across all compressible surfaces; preserve
-- no artificial sink on paved roads and preserve the vanilla target.
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
assert(normal>1.35 and normal<=1.45,"Cultivated sink +40% baseline regression")
assert(heavy>normal,"Extra load should produce extra sink")
assert(wet>normal,"Wet soil should produce extra sink")
assert(crawled<normal,"Crawler distribution should reduce sink")
local plowed=measureSink(2,10,0,false,false)
assert(plowed>1.49 and plowed<1.51,"Plowed dry reference should be +50% vanilla")
assert(plowed>normal,"Plowed should sink more than cultivated")
assert(measureSink(2,30,1,false,false)<=1.95,"Heavy wet plowed sink must cap")
assert(measureSink(4,10,0,false,false)>1,"Firm field sink boost missing")
assert(measureSink(1,10,0,false,true)>1,"Snow surface sink boost missing")
assert(measureSink(0,10,0,false,false)==1,"Road should not artificially sink")
assert(measureSink(0,30,1,false,false)==1,"Loaded wet road should not artificially sink")
-- Hard and uncategorized terrain receive an ARS boost only when GIANTS
-- provides a positive base MAX_SINK (the native zero target remains zero).
WheelsUtil.getGroundType=function() return WheelsUtil.GROUND_HARD_TERRAIN end
assert(measureSink(0,10,0,false,false)>1.05,"Hard ground native positive sink not boosted")
WheelsUtil.getGroundType=function() return 999 end
assert(measureSink(0,10,0,false,false)>1,"Other ground native positive sink not boosted")
WheelsUtil.MAX_SINK = nil
WheelPhysics.MAX_SINK[0]=0
local v={isServer=true,isAddedToPhysics=true}
WheelPhysics.updateSink({vehicle=v,densityType=0},16,0)
assert(WheelPhysics.MAX_SINK[0]==0,"Native zero-sink ground was modified")
print("PASS: native target ~1.50x on plowed; soil/load/wet/crawler, zero road, globals restored")
-- Native visual ground displacement, distinct from physical sink:
-- reuse the real serverUpdate hook and assert native setter call path.
local nativeCalls = {}
WheelPhysics.serverUpdate = function(wp,dt,index,wet)
    nativeCalls[#nativeCalls+1]={"server",dt}
end
ARSPhysics.hooksInstalled=false
ARSPhysics:installHooks()
Platform={gameplay={wheelTerrainDisplacement=true}}
WheelsUtil.getGroundType=function() return WheelsUtil.GROUND_ROAD end
local function visualWheel(groundCode,mass,tireType,wet)
    WheelsUtil.getGroundType=function() return groundCode end
    local v={isServer=true,isAddedToPhysics=true,
        spec_wheels={wheels={{},{},{},{}}},getTotalMass=function() return mass end}
    local wp={vehicle=v,wheel={node=10},wheelShape=12,displacementScale=1,
        supportsWheelSink=true,displacementAllowed=true, densityType=0,
        tireType=tireType, wheelShapeWidth=0.6, hasGroundContact=true}
    local written={}
    wp.setDisplacementAllowed=function(self,allowed)
        written[#written+1]=self.displacementScale
    end
    WheelPhysics.serverUpdate(wp,16,1,wet)
    return wp,written
end
local road,writesRoad=visualWheel(WheelsUtil.GROUND_ROAD,30,1,1)
assert(road.displacementScale==1 and #writesRoad==0,"Road must remain vanilla")
local plowed,writesPlowed=visualWheel(WheelsUtil.GROUND_HARD_TERRAIN,10,1,0)
assert(plowed.displacementScale > 1 and plowed.displacementScale < 2.0)
assert(#writesPlowed==1,"Native setter not called for terrain")
local originalScale=plowed.displacementScale
WheelsUtil.getGroundType=function() return WheelsUtil.GROUND_ROAD end
WheelPhysics.serverUpdate(plowed,16,1,0)
assert(plowed.displacementScale==1,"Road must restore original terrain displacement")
local softHeavy,writesHeavy=visualWheel(WheelsUtil.GROUND_SOFT_TERRAIN,30,1,1)
assert(softHeavy.displacementScale<=2.5 and softHeavy.displacementScale>originalScale)
assert(#writesHeavy==1,"Expected native setter update on loaded soft terrain")
local softCrawler,writesCrawler=visualWheel(WheelsUtil.GROUND_SOFT_TERRAIN,30,2,1)
assert(softCrawler.displacementScale<softHeavy.displacementScale,"Crawler must reduce deformation")
-- Field cultivation actually comes from native densityType, not guessed terrain.
local plowedVisual,writesField=visualWheel(WheelsUtil.GROUND_HARD_TERRAIN,10,1,0)
plowedVisual.densityType=FieldGroundType.PLOWED
WheelPhysics.serverUpdate(plowedVisual,16,1,0)
assert(plowedVisual.displacementScale==2.25,"Plowed field should reach visual 2.25x at neutral wheel load")
local otherField,writesOther=visualWheel(WheelsUtil.GROUND_HARD_TERRAIN,10,1,0)
otherField.densityType=FieldGroundType.GRASS
WheelPhysics.serverUpdate(otherField,16,1,0)
assert(otherField.displacementScale<plowedVisual.displacementScale,"Cultivation state must affect terrain displacement")
local missing,writesMissing=visualWheel(WheelsUtil.GROUND_SOFT_TERRAIN,30,1,1)
missing.supportsWheelSink=false
WheelPhysics.serverUpdate(missing,16,1,1)
assert(missing.displacementScale==1,"Unsupported native wheel sink must be skipped")
Platform.gameplay.wheelTerrainDisplacement=false
WheelPhysics.serverUpdate(softHeavy,16,1,1)
assert(softHeavy.displacementScale==1,"Disabled native gameplay terrain deformation must restore")
print("PASS: GIANTS terrain ruts, collision guard, road restore, load/crawler")
-- Verify the actual extraSinkSupported gate is enabled BEFORE vanilla
-- serverUpdate. This missing GIANTS flag was the original invisible-sink gap.
local nativeSeen={}
WheelPhysics.serverUpdate=function(wp,dt,index,wet)
    -- Mock real GIANTS: gate already enabled before vanilla serverUpdate,
    -- but contact-aware extraSinkMaxValue is set INSIDE the updateSink hook.
    if wp.extraSinkSupported then
        WheelPhysics.updateSink(wp,dt,wet)
    end
    nativeSeen[#nativeSeen+1]={supported=wp.extraSinkSupported,
        max=wp.extraSinkMaxValue}
end
ARSPhysics.hooksInstalled=false
ARSPhysics:installHooks()
Platform.gameplay.wheelTerrainDisplacement=true
WheelsUtil.getGroundType=function() return WheelsUtil.GROUND_HARD_TERRAIN end
local eVehicle={isServer=true,isAddedToPhysics=true,
    spec_wheels={wheels={{},{},{},{}}},
    getTotalMass=function() return 20 end}
local extraWheel={vehicle=eVehicle,wheel={node=10},wheelShape=12,
    radius=1,extraSinkSupported=false,extraSinkMaxValue=0.2,
    densityType=FieldGroundType.PLOWED,displacementScale=1,
    displacementAllowed=true,supportsWheelSink=true,
    tireType=1,wheelShapeWidth=0.6}
extraWheel.setDisplacementAllowed=function(self) end
WheelPhysics.serverUpdate(extraWheel,16,1,0)
assert(nativeSeen[#nativeSeen].supported==true,"Native GIANTS sink gate not enabled")
assert(nativeSeen[#nativeSeen].max>=0.24 and nativeSeen[#nativeSeen].max<=0.34,
    "Plowed native cap not recalibrated for rim-line goal")
assert(extraWheel.displacementScale>=2.2 and extraWheel.displacementScale<=2.5,
    "Plowed native visual terrain factor too weak")
WheelsUtil.getGroundType=function() return WheelsUtil.GROUND_ROAD end
extraWheel.densityType=FieldGroundType.NONE
WheelPhysics.serverUpdate(extraWheel,16,1,0)
assert(nativeSeen[#nativeSeen].max==0,"Native road must not be additionally sunken")
assert(extraWheel.displacementScale==1,"Road visual must be vanilla")
local oldEnabled=ARS.isEnabled
ARS.isEnabled=function() return false end
WheelPhysics.serverUpdate(extraWheel,16,1,0)
assert(nativeSeen[#nativeSeen].supported==false and
    nativeSeen[#nativeSeen].max==0.2,
    "Disabling ARS must restore native extra sink support and cap")
ARS.isEnabled=oldEnabled
ARSPhysics.restore()
assert(extraWheel.extraSinkSupported==false and extraWheel.extraSinkMaxValue==0.2,
    "Map unload must restore native sink values")
assert(extraWheel.displacementScale==1,"Map unload must restore visual scale")
assert(VehicleMotor.getTorqueAndSpeedValues==motorFn,"Native torque changed")
print("PASS: native GIANTS extra-sink gate, bounded plowed depth, road, restore")
print("PASS: rim-horn targeted physical native sink and untouched motor torque")
-- Per-wheel rim and load regressions preserve motor, rolling, and draft paths.
-- The native updateSink mock records the temporarily raised limit.
local function rimCase(width,rimDiameter,crawler,load)
    local v={isServer=true,isAddedToPhysics=true,
        spec_wheels={wheels={{},{},{},{}}},
        getTotalMass=function() return 10 end}
    local w={node=10,visualWheels=rimDiameter and {{rimDiameter=rimDiameter}} or {}}
    local wp={vehicle=v,wheel=w,wheelShape=12,
        radius=0.92,radiusOriginal=0.92,
        extraSinkSupported=false,extraSinkMaxValue=0.184,
        densityType=FieldGroundType.PLOWED,displacementScale=1,
        displacementAllowed=true,supportsWheelSink=true,
        wheelShapeWidth=width,tireType=crawler and 2 or 1}
    wp.setDisplacementAllowed=function() end
    wp.wheelShapeCreated=true
    wp.getTireLoad=function() return load end
    local original=WheelPhysics.MAX_SINK[FieldGroundType.PLOWED]
    -- GIANTS simulation: original mock records actual temporary MAX_SINK.
    WheelPhysics.serverUpdate(wp,16,1,0)
    assert(sinkSeen[#sinkSeen] >= wp.extraSinkMaxValue - 0.0001,
        "Temporary native MAX_SINK must actually reach rim target")
    assert(WheelPhysics.MAX_SINK[FieldGroundType.PLOWED]==original,
        "Class-global MAX_SINK must be restored after every wheel")
    return wp
end
WheelsUtil.getGroundType=function() return WheelsUtil.GROUND_HARD_TERRAIN end
g_updateLoopIndex=615
local narrow=rimCase(0.38,1.18,false,6)
local wide=rimCase(1.15,1.18,false,6)
local crawler=rimCase(0.38,1.18,true,6)
local limit=(0.92-1.18/2)*0.90
assert(math.abs(narrow.extraSinkMaxValue-limit)<0.001,
    "Narrow tyre should approach, but not cross, physical rim horn")
assert(wide.extraSinkMaxValue<narrow.extraSinkMaxValue,
    "Wide tyres need lower physical sink target")
assert(crawler.extraSinkMaxValue<narrow.extraSinkMaxValue,
    "Crawler sink needs further reduction")
local fallback=rimCase(0.38,nil,false,6)
assert(fallback.extraSinkMaxValue<=0.92*0.34+0.0001,
    "No-rim-data fallback must stay conservative")
print("PASS: rim geometry, narrow/wide/crawler and fallback guards")
