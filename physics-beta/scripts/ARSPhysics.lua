-- ARS Physics / Farming Simulator 25
-- The Man, The Myth, The Legend : KeilerHirsch
-- Independent ARS Physics curves built on GIANTS-native systems.
-- Correct GIANTS vanilla physics inputs; no vehicle controls, HUD or maintenance.
-- GDN FS25 script/engine v1.20: WheelPhysics, WheelsUtil, PowerConsumer.

ARSPhysics = { VERSION = "0.1.18.9", hooksInstalled = false }

-- Relative to GIANTS vanilla = 1.00. No second physics engine.
-- Tune by soil class in one place; only active surface is evaluated.
local PROFILES = {
    other      = { grip=1.000, sink=1.025, rolling=1.000, draft=1.000 },
    road       = { grip=1.000, sink=1.000, rolling=1.000, draft=1.000 },
    hard       = { grip=1.000, sink=1.025, rolling=1.000, draft=1.000 },
    firm       = { grip=1.015, sink=1.045, rolling=1.020, draft=1.000 },
    field      = { grip=1.030, sink=1.095, rolling=1.035, draft=1.000 },
    cultivated = { grip=1.045, sink=1.160, rolling=1.055, draft=1.025 },
    plowed     = { grip=1.020, sink=1.200, rolling=1.080, draft=1.055 },
    seedbed    = { grip=1.045, sink=1.145, rolling=1.045, draft=1.015 },
    soft       = { grip=0.975, sink=1.220, rolling=1.095, draft=1.045 },
    snow       = { grip=1.000, sink=1.060, rolling=1.000, draft=1.000 }
}

local CFG = {
    gripMin=0.90, gripMax=1.14,
    sinkMin=1.00, sinkMax=3.15, sinkGain=8.20,
    rollingMin=0.97, rollingMax=1.22,
    draftMin=0.84, draftMax=1.17
}

local function clamp(v, low, high)
    if type(v) ~= "number" or v ~= v then return low end
    return math.max(low, math.min(high, v))
end

local function fieldState(densityType)
    if FieldGroundType == nil or densityType == nil
        or densityType == FieldGroundType.NONE then return "other" end

    local groups = {
        plowed     = { "PLOWED", "PLOUGHED", "RIDGE" },
        cultivated = { "CULTIVATED", "CULTIVATED_WITH_STUBBLE", "STUBBLE_TILLAGE" },
        seedbed    = { "SEEDBED", "SOWN", "SOWN_WITH_STUBBLE" },
        firm       = { "GRASS", "GRASS_CUT", "HARVEST_READY", "HARVEST_READY_OTHER" }
    }
    for _, category in ipairs({ "plowed", "cultivated", "seedbed", "firm" }) do
        for _, key in ipairs(groups[category]) do
            if FieldGroundType[key] ~= nil and densityType == FieldGroundType[key] then
                return category
            end
        end
    end
    return "field"
end

local function groundState(wp)
    if wp == nil then return "other" end
    if wp.hasSnowContact then return "snow" end
    local field = fieldState(wp.densityType)
    if field ~= "other" then return field end
    if WheelsUtil == nil or WheelsUtil.getGroundType == nil
        or WheelContactType == nil then return "other" end

    local code = WheelsUtil.getGroundType(false,
        wp.contact ~= WheelContactType.GROUND, wp.groundDepth or 0)
    if code == WheelsUtil.GROUND_ROAD then return "road" end
    if code == WheelsUtil.GROUND_SOFT_TERRAIN then return "soft" end
    if code == WheelsUtil.GROUND_HARD_TERRAIN then return "hard" end
    return "other"
end

local function wheelLoad(wp)
    local wheel = wp.wheel
    local vehicle = wp.vehicle
    local width = clamp(wp.wheelShapeWidth or 0.6, 0.25, 1.5)
    local tons = nil

    if type(getWheelShapeContactForce) == "function"
        and wheel ~= nil and wheel.node ~= nil
        and wp.wheelShape ~= nil and wp.wheelShape ~= 0
        and wp.hasGroundContact then
        -- If this GIANTS API fails for a valid wheel, keep its traceback in log.
        local forceKn = getWheelShapeContactForce(wheel.node, wp.wheelShape)
        if type(forceKn) == "number" and forceKn > 0 then
            tons = forceKn / 9.81
        end
    end

    if tons == nil and vehicle ~= nil and vehicle.getTotalMass ~= nil then
        local count = vehicle.spec_wheels and vehicle.spec_wheels.wheels
            and #vehicle.spec_wheels.wheels or 4
        tons = vehicle:getTotalMass(true) / math.max(1, count)
    end
    tons = clamp(tons or 2.5, 0.2, 15)
    -- Reference 2.5 tons per 0.6m tire: an index, not a soil-pressure claim.
    local footprintIndex = clamp((tons / 2.5) * (0.6 / width), 0.45, 2.2)
    return width, tons, footprintIndex
end

local function isCrawler(wp)
    -- Only trust the registered GIANTS tire type; never guess by vehicle name.
    if WheelsUtil == nil or WheelsUtil.getTireTypeName == nil or wp.tireType == nil then
        return false
    end
    local name = WheelsUtil.getTireTypeName(wp.tireType)
    return type(name) == "string" and string.upper(name) == "CRAWLER"
end

local function profileFor(wp)
    return PROFILES[groundState(wp)] or PROFILES.other
end

local function gripFactor(wp, wet)
    local surface = groundState(wp)
    local p = PROFILES[surface] or PROFILES.other
    if surface == "road" or surface == "hard" or surface == "other"
        or surface == "snow" then return 1 end

    local width, _, loadIndex = wheelLoad(wp)
    -- Moderate load/width correction. No wheel slip sampling.
    local widthIndex = clamp((width - 0.6) / 0.6, -0.5, 1.0)
    local soft = surface == "cultivated" or surface == "plowed"
        or surface == "seedbed" or surface == "soft"
    local correction = (soft and 1 or 0.5)
        * (0.035 * widthIndex - 0.025 * (loadIndex - 1))
    local track = isCrawler(wp) and soft and 0.018 or 0
    -- Wet/snow primary friction coefficients remain GIANTS-owned.
    -- Wetness only moderates the extra track advantage, not vanilla wet grip.
    track = track * (1 - 0.35 * clamp(wet or 0, 0, 1))
    return clamp(p.grip + correction + track, CFG.gripMin, CFG.gripMax)
end

local function sinkFactor(wp, wet)
    local surface = groundState(wp)
    local p = PROFILES[surface] or PROFILES.other
    if p.sink == 1 then return 1 end

    local _, _, loadIndex = wheelLoad(wp)
    local wetness = clamp(wet or 0, 0, 1)
    local load = clamp(1 + 0.085 * (loadIndex - 1), 0.92, 1.11)
    local moisture = 1 + (surface == "firm" and 0.025 or 0.070) * wetness
    -- Tracks spread ground pressure; do not count track contact as a wide tire.
    local track = isCrawler(wp) and 0.94 or 1
    -- Amplify ONLY ARSPhysics's additional sink relative to GIANTS vanilla.
    -- Preserve soil, wheel-load, weather and crawler weighting; increase
    -- ground response while preserving native asphalt and zero-sink surfaces.
    -- This avoids doubling the absolute GIANTS sink distance on every surface.
    local weighted = p.sink * load * moisture * track
    local extra = math.max(0, weighted - 1)
    return clamp(1 + CFG.sinkGain * extra, CFG.sinkMin, CFG.sinkMax)
end

local function currentWetness()
    local weather = g_currentMission ~= nil and g_currentMission.environment
        and g_currentMission.environment.weather
    if weather ~= nil and weather.getGroundWetness ~= nil then
        return clamp(weather:getGroundWetness() or 0, 0, 1)
    end
    return 0
end

-- GIANTS native wheel terrain displacement: this drives physical terrain
-- deformation / visible wheel ruts, NOT the visual wheel transform or motor.
-- 1.50 = at most +50% of the stock terrain displacement input.
local VISUAL_DISPLACEMENT = {
    other=0.10, road=0.00, hard=0.08, firm=0.16, field=0.25,
    cultivated=0.40, plowed=0.50, seedbed=0.35, soft=0.50, snow=0.22
}

local function visualDisplacementFactor(wp, wet)
    local surface = groundState(wp)
    if surface == "road" or wp.hasWaterContact then return 1 end
    local strength = VISUAL_DISPLACEMENT[surface] or 0
    if strength <= 0 then return 1 end
    local _, _, loadIndex = wheelLoad(wp)
    local load = clamp(1 + 0.18 * (loadIndex - 1), 0.82, 1.18)
    local moisture = 1 + 0.20 * clamp(wet or 0, 0, 1)
    local track = isCrawler(wp) and 0.88 or 1
    return 1 + clamp(strength * load * moisture, 0, 0.50) * track
end

-- Restore the original scale when ARS is disabled or the wheel reaches
-- non-deformable ground. This is per wheel, with no global GIANTS constants.
local originalDisplacement = setmetatable({}, {__mode="k"})
local function rollingFactor(wp)
    local surface = groundState(wp)
    local p = PROFILES[surface] or PROFILES.other
    if surface == "road" or surface == "hard" then
        -- Subtle paved-ground response, never additional mass or an engine buff.
        -- Per-wheel contact load (or vehicle-only mass fallback) includes fill
        -- weight for any wheeled vehicle/implement, including trailers.
        local _, _, loadIndex = wheelLoad(wp)
        local loadExtra = clamp((loadIndex - 0.75) / 1.45, 0, 1)
        -- GIANTS already handles primary wet tire friction; this only adds a
        -- tiny rolling penalty on damp pavement, with a strict 1.6% cap.
        return 1 + 0.012 * loadExtra + 0.004 * currentWetness()
    end
    if p.rolling == 1 then return 1 end
    local _, _, loadIndex = wheelLoad(wp)
    -- GIANTS already includes trailer and cargo mass in the wheel physics.
    -- Keep soil and wheel-load responses; avoid an extra trailer-class tax.
    local load = 1 + 0.032 * (loadIndex - 1)
    local track = isCrawler(wp) and -0.018 or 0
    return clamp(p.rolling * load + track,
        CFG.rollingMin, CFG.rollingMax)
end


-- Works with the actual ground under the working implement when available.
local function implementGround(tool)
    -- FS25 engine: getDensityAtWorldPos(mapId, x, y, z) returns packed bits.
    -- No FSDensityMapUtil.getFieldDataAtWorldPosition (not a FS25 API).
    local spec = tool and tool.spec_powerConsumer
    local mission = g_currentMission
    if spec == nil or spec.forceNode == nil or mission == nil
        or mission.fieldGroundSystem == nil or getDensityAtWorldPos == nil
        or getWorldTranslation == nil or FieldDensityMap == nil
        or FieldGroundType == nil or FieldGroundType.getTypeByValue == nil
        or bit32 == nil then return "other" end

    local mapId, first, count = mission.fieldGroundSystem:getDensityMapData(
        FieldDensityMap.GROUND_TYPE)
    if mapId == nil or first == nil or count == nil then return "other" end
    local x, y, z = getWorldTranslation(spec.forceNode)
    local bits = getDensityAtWorldPos(mapId, x, y, z)
    if type(bits) ~= "number" then return "other" end
    local value = bit32.band(bit32.rshift(bits, first), 2 ^ count - 1)
    return fieldState(FieldGroundType.getTypeByValue(value))
end
local function hasActiveWorkArea(tool)
    local spec = tool.spec_workArea
    if type(spec) ~= "table" or type(spec.workAreas) ~= "table"
        or type(tool.getIsWorkAreaActive) ~= "function" then return false end

    for _, workArea in pairs(spec.workAreas) do
        if type(workArea) == "table" then
            local ok, active = pcall(tool.getIsWorkAreaActive, tool, workArea)
            if not ok then
                if not ARSPhysics.workAreaStatusWarning then
                    print("[ARS Physics] Work area state unavailable; extra draft disabled: "..tostring(active))
                    ARSPhysics.workAreaStatusWarning = true
                end
                return false
            end
            if active == true then return true end
        end
    end
    return false
end

local function draftFactor(tool)
    local isWorkImplement = tool.spec_plow ~= nil
        or tool.spec_subsoiler ~= nil
        or tool.spec_cultivator ~= nil
        or tool.spec_sowingMachine ~= nil
        or tool.spec_planter ~= nil
        or tool.spec_powerHarrow ~= nil
        or tool.spec_rotaryHarrow ~= nil
    if not isWorkImplement then return 1 end
    if not hasActiveWorkArea(tool) then return 1 end

    local p = PROFILES[implementGround(tool)] or PROFILES.other
    -- GIANTS selects maxForce from the implement XML configuration, then its
    -- PowerConsumer callback derives resistance from mass, speed and dt.
    -- Keep that limit as the baseline. ARS applies only an existing positive
    -- soil draft increment; it does not guess force from tool class or speed.
    return clamp(math.max(1, p.draft), 1, CFG.draftMax)
end

-- Optional developer-console tuning; no HUD, no user config, no persistence.
-- Restricted to the authoritative game server (including single player).
function ARSPhysics:consoleCurve(surface, grip, sink, rolling, draft)
    if g_server == nil then return "[ARS Physics] Server only" end
    local p = PROFILES[surface or ""]
    if p == nil then return "[ARS Physics] Usage: arsCurve <soil> [grip sink rolling draft]" end
    if grip == nil then
        return string.format("[ARS Physics] %s: %.3f %.3f %.3f %.3f",
            surface, p.grip, p.sink, p.rolling, p.draft)
    end
    local a, b, c, d = tonumber(grip), tonumber(sink), tonumber(rolling), tonumber(draft)
    if a == nil or b == nil or c == nil or d == nil then
        return "[ARS Physics] Give four numbers (grip sink rolling draft)"
    end
    p.grip = clamp(a, CFG.gripMin, CFG.gripMax)
    p.sink = clamp(b, CFG.sinkMin, CFG.sinkMax)
    p.rolling = clamp(c, CFG.rollingMin, CFG.rollingMax)
    p.draft = clamp(d, CFG.draftMin, CFG.draftMax)
    return self:consoleCurve(surface)
end

function ARSPhysics:installHooks()
    if self.hooksInstalled then return end
    if WheelPhysics == nil or PowerConsumer == nil
        or type(WheelPhysics.updateFriction) ~= "function"
        or type(WheelPhysics.updateSink) ~= "function"
        or type(WheelPhysics.updatePhysics) ~= "function"
        or type(PowerConsumer.onUpdate) ~= "function" then
        print("[ARS Physics] Missing FS25 physics hooks; no changes installed")
        return
    end

    local vanillaFriction = WheelPhysics.updateFriction
    WheelPhysics.updateFriction = function(wp, dt, wet)
        vanillaFriction(wp, dt, wet)
        if not ARS:isEnabled("physics") then
            ARSPhysics.restoreWheel(wp)
            return
        end
        if wp.vehicle == nil or not wp.vehicle.isServer
            or not wp.vehicle.isAddedToPhysics
            or wp.vehicle.getLastSpeed == nil or wp.vehicle:getLastSpeed() <= 0.2
            or WheelsUtil == nil or WheelsUtil.getTireFriction == nil
            or FieldGroundType == nil or WheelContactType == nil
            or wp.tireType == nil then return end

        local snow = wp.hasSnowContact and 1 or 0
        local wetValue = snow == 1 and 0 or clamp(wet or 0, 0, 1)
        local isField = wp.densityType ~= nil
            and wp.densityType ~= FieldGroundType.NONE
        local terrain = WheelsUtil.getGroundType(isField,
            wp.contact ~= WheelContactType.GROUND, wp.groundDepth or 0)
        local tireData = WheelsUtil.tireTypes
            and WheelsUtil.tireTypes[wp.tireType]
        if tireData == nil then return end

        local base = WheelsUtil.getTireFriction(wp.tireType, terrain, wetValue, snow)
        if type(base) ~= "number" then return end
        local target = base * gripFactor(wp, wetValue)
        if math.abs((wp.tireGroundFrictionCoeff or base) - target) > 0.004 then
            ARSPhysics.touched[wp] = {base=base, target=target}
            wp.tireGroundFrictionCoeff = target
            wp.isFrictionDirty = true -- GIANTS reapplies it with the correct 6-arg API
        end
    end

    -- After GIANTS has refreshed its native contact classification, update
    -- only its wheel terrain-displacement input (1.00x .. 1.50x).
    local vanillaServerUpdate = WheelPhysics.serverUpdate
    WheelPhysics.serverUpdate = function(wp, dt, currentUpdateIndex, wet)
        vanillaServerUpdate(wp, dt, currentUpdateIndex, wet)

        if wp.vehicle == nil or not wp.vehicle.isServer
            or not wp.vehicle.isAddedToPhysics
            or wp.wheel == nil or type(wp.wheelShape) ~= "number"
            or wp.wheelShape == 0
            or type(wp.displacementScale) ~= "number"
            or type(wp.setDisplacementAllowed) ~= "function" then return end

        local base = originalDisplacement[wp]
        if base == nil then
            base = wp.displacementScale
            originalDisplacement[wp] = base
        end

        local nativeEnabled = Platform ~= nil and Platform.gameplay ~= nil
            and Platform.gameplay.wheelTerrainDisplacement == true
            and wp.supportsWheelSink ~= false and wp.displacementAllowed ~= false
        local factor = 1
        if nativeEnabled and ARS:isEnabled("physics") then
            factor = visualDisplacementFactor(wp, wet)
        end
        local target = base * factor
        -- Noise from contact loads must not trigger a native wheel update
        -- every frame. Restore 1.00x immediately when leaving deformable soil.
        if math.abs(wp.displacementScale - target) >= 0.025
            or (factor == 1 and wp.displacementScale ~= base) then
            wp.displacementScale = target
            wp:setDisplacementAllowed(wp.displacementAllowed)
        end
    end
    local vanillaSink = WheelPhysics.updateSink
    WheelPhysics.updateSink = function(wp, dt, wet)
        if not ARS:isEnabled("physics") then return vanillaSink(wp, dt, wet) end
        local list = WheelPhysics.MAX_SINK
        local key = wp.densityType
        local raw = list ~= nil and key ~= nil and list[key] or nil
        if not wp.vehicle or not wp.vehicle.isServer
            or not wp.vehicle.isAddedToPhysics or type(raw) ~= "number"
            or raw <= 0 or wp.hasWaterContact then
            return vanillaSink(wp, dt, wet)
        end

        -- Temporarily substitute the stock target; original GIANTS controls
        -- the interpolation, wheel geometry and network behavior.
        list[key] = raw * sinkFactor(wp, wet)
        return ARS.callWithRestore(function()
            list[key] = raw
        end, vanillaSink, wp, dt, wet)
    end

    local vanillaWheelPhysics = WheelPhysics.updatePhysics
    WheelPhysics.updatePhysics = function(wp, brakeForce, torque)
        if not ARS:isEnabled("physics") then return vanillaWheelPhysics(wp, brakeForce, torque) end
        if wp.vehicle == nil or not wp.vehicle.isServer
            or not wp.vehicle.isAddedToPhysics
            or type(wp.rotationDamping) ~= "number" then
            return vanillaWheelPhysics(wp, brakeForce, torque)
        end
        local base = wp.rotationDamping
        wp.rotationDamping = base * rollingFactor(wp)
        return ARS.callWithRestore(function()
            wp.rotationDamping = base
        end, vanillaWheelPhysics, wp, brakeForce, torque)
    end

    local vanillaConsumer = PowerConsumer.onUpdate
    PowerConsumer.onUpdate = function(tool, dt, ...)
        if not ARS:isEnabled("physics") then return vanillaConsumer(tool, dt, ...) end
        local spec = tool.spec_powerConsumer
        if not tool.isServer or not tool.isActive or spec == nil
            or type(spec.maxForce) ~= "number" or spec.maxForce <= 0 then
            return vanillaConsumer(tool, dt, ...)
        end
        local original = spec.maxForce
        spec.maxForce = original * draftFactor(tool)
        return ARS.callWithRestore(function()
            spec.maxForce = original
        end, vanillaConsumer, tool, dt, ...)
    end

    -- Native GIANTS torque curve remains unchanged (1.00x); no motor hook.

    self.hooksInstalled = true
    ARS.available.physics = true
    print("[ARS Physics] Grip, sink, native wheel-displacement visuals, rolling and tool resistance installed; motor torque unchanged")
end

-- Shared read-only classification; no second set of soil constants.
ARSPhysics.groundState = groundState
ARSPhysics.implementGround = implementGround
ARSPhysics.touched = setmetatable({}, {__mode="k"})
function ARSPhysics.restoreWheel(wp)
    local entry=ARSPhysics.touched[wp]
    if entry~=nil then
        if wp.tireGroundFrictionCoeff==entry.target then
            wp.tireGroundFrictionCoeff=entry.base
            wp.isFrictionDirty=true
        end
        ARSPhysics.touched[wp]=nil
    end
end
function ARSPhysics.restore()
    for wp in pairs(ARSPhysics.touched) do ARSPhysics.restoreWheel(wp) end
end
