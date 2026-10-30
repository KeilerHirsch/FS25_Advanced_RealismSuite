# ARS Physics Beta RC6 – RIMLINE (30.10.2026)

**Engineering candidate, not a public release.** Built from RC5 commit `c22d2e9` in isolated worktree. Internal mod version remains `0.1.18.9`, RC6 is identified by its ZIP filename. No public push.

## Goal
Dry, freshly plowed ground: narrow maintenance tyres may sink visibly to just below the red outer rim horn, while keeping RC5 grip, rolling, draft, motor and gearbox behavior unchanged. Do not interpret sink as a guaranteed visual distance on every map.

## Native implementation
- GIANTS `WheelVisual.rimDiameter` (from `.outerRim(0)#widthAndDiam`) is used with `WheelPhysics.radiusOriginal` to estimate physical sidewall: `R - rimDiameter/2`. The target is limited to **90% of physical sidewall**, max **42% of wheel radius**, max **0.38 m**. When rim diameter is missing/invalid, fallback <= **34% of radius**. Crawlers <= **20% of radius**.
- Base per-surface requested depths before load/width/wetness: plowed **0.310 m**, soft **0.335 m**, cultivated **0.190 m**, seedbed **0.170 m**, field **0.105 m**; firm, snow, road keep small/zero RC5 levels.
- Width proxy: narrow tyres sink deeper than wide/dual shared WheelShapes; weighted current `getTireLoad()` where available; wetness uses only actual GIANTS weather input (no heat-to-wetness inference). Tracks reduce sinking.
- Keep native `WheelPhysics.updateSink()` interpolation/contact/speed/visual/network path. Native `sinkTarget = min(WheelPhysics.MAX_SINK[densityType], extraSinkMaxValue)` needs BOTH bounds lifted: temporarily lift an *existing positive* density MAX_SINK entry to the wheel-specific capped target while running original `updateSink()`; restore it immediately, including on error via `ARS.callWithRestore`. Do not create missing/zero density entries or permanently modify GIANTS global physics.
- No manual mesh offset, direct radius mutation, suspension changes, extra drag, more torque, or separate terrain heightmap journal. Existing wheel-displacement factors, native collision guard, RC5 road/unload reset and native load cache remain.
- Rim geometry is a robust approximation, not exact photographic rim profile. Avoid claiming exact physical sink in FS25 until actual game A/B test.

## Reference research
- GIANTS GDN FS25 `WheelVisual:loadFromXML` officially exposes `rimDiameter`: https://gdn.giants-software.com/documentation_scripting_fs25.php?category=93&class=911&version=script
- GIANTS `WheelPhysics:updateSink()`, `WheelPhysics:updateBase()` via https://github.com/grevef/fs25-lua-apis/blob/main/vehicles/wheels/WheelPhysics.lua
- Historical REA Wheels GIANTS forum sink mod snippet (0.20 m, not directly FS25-verified): https://forum.giants-software.com/viewtopic.php?start=75&t=157507
- Deep Ruts uses native `displacementScale` 1.75x / 2.25x / 2.5x: https://github.com/SecondChanceGaming3709/FS25_DeepRutts
- Visual Mud Tracks uses effective radius, different approach with additional state/persistence; approach not copied: https://www.kingmods.net/de/ls25/mods/79740/visuelle-schlammspuren

## Validation and operational limits
Lua 5.1 syntax, RC5 regression suite and RC6 rim, width, crawler, conservative-fallback and native global-restore assertions must pass before packaging. Review mod ZIP root structure, SHA256 and make exactly one ARS Physics ZIP active. Close game before swap. Back up RC5. Runtime LS25 play, dedicated multiplayer and ADS temperature remain untested in RC6. No external third-party code copied.
