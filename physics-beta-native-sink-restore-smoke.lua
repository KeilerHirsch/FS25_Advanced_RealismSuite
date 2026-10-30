-- Regression: GIANTS FS25 WheelPhysics.updateSink assigns sink = sinkTarget
-- when the wheel is parked. A zeroed target would snap the wheel upwards.
ARS = {available={}, isEnabled=function() return true end}
ARS.callWithRestore = function(cleanup,callback,...)
    local ok,result = pcall(callback,...)
    cleanup()
    assert(ok,result)
    return result
end
Platform = {gameplay={wheelTerrainDisplacement=true}}
FieldGroundType = {NONE=0}
WheelContactType = {NONE=0,GROUND=1}
WheelsUtil = {
    GROUND_ROAD=101,
    getGroundType=function() return 101 end
}
PowerConsumer = {onUpdate=function() end}
local nativeCalls = 0
WheelPhysics = {
    MAX_SINK={[0]=0},
    updateFriction=function() end,
    updatePhysics=function() end,
    updateSink=function(wp,dt,wet)
        nativeCalls = nativeCalls+1
        -- Stock GIANTS branch at contact and <=0.3 km/h:
        -- no new sink target computed, but sink is assigned to sinkTarget.
        assert(wp.vehicle:getLastSpeed() <= 0.3)
        if math.abs(wp.sink-wp.sinkTarget)>0.001 then
            wp.sink=wp.sinkTarget
            wp.deltaY=wp.deltaYOriginal+wp.sink
            wp.isPositionDirty=true
        end
    end,
    serverUpdate=function(wp,dt,index,wet)
        if wp.extraSinkSupported then WheelPhysics.updateSink(wp,dt,wet) end
    end
}
dofile("physics-beta/scripts/ARSPhysics.lua")
ARSPhysics:installHooks()
local wheel={
    vehicle={
        isServer=true,isAddedToPhysics=true,
        getLastSpeed=function() return 0 end
    },
    wheel={node=11},wheelShape=12,
    radius=1,radiusOriginal=1,
    densityType=FieldGroundType.NONE, contact=WheelContactType.GROUND,
    extraSinkSupported=false,extraSinkMaxValue=0.2,
    supportsWheelSink=true,displacementAllowed=true,displacementScale=1,
    deltaYOriginal=0.05,deltaY=0.15,sink=0.10,sinkTarget=0.10
}
wheel.setDisplacementAllowed=function() end
local previous=wheel.sink
for i=1,7 do
    WheelPhysics.serverUpdate(wheel,100,1,0)
    assert(wheel.sink<=previous and wheel.sink>=0,
        "Stopped wheel must move smoothly toward ground level")
    assert(wheel.sinkTarget==wheel.sink,
        "Native sinkTarget must follow progressive reset, not snap to zero")
    assert(math.abs(wheel.deltaY-wheel.deltaYOriginal-wheel.sink)<0.000001,
        "WheelShape deltaY and physical sink must agree")
    if i==1 then
        assert(wheel.sink>0.08 and wheel.sink<0.1,
            "First native update snapped wheel to zero")
    end
    previous=wheel.sink
end
assert(nativeCalls==7,"Original GIANTS sink path must execute once per tick")
assert(WheelPhysics.MAX_SINK[0]==0,"Do not invent native sink on paved roads")
ARSPhysics.restore()
assert(wheel.sink==0 and wheel.deltaY==wheel.deltaYOriginal,
    "Unload cleanup must restore original position")
print("PASS: parked-wheel native sinkTarget/deltaY gradual restore without snap")
