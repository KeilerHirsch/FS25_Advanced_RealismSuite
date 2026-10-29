# ARS Physics Beta

**Advanced Realism Suite — experimental Farming Simulator 25 physics module.**

This standalone beta modifies the native GIANTS driving-physics calculations:
terrain-dependent tire grip, wheel sinking influenced by soil condition, wetness,
wheel load and tire setup, rolling resistance, implement draft and pulling performance.
It is **not** the full Advanced Realism Suite.

## Installation
Place the ZIP file from the matching GitHub release in your FS25 mods folder,
enable ARS Physics Beta in the savegame selection, and test on a **backup save**.
Every version-coded ZIP uses a new FS25 mod ID; enable the new version explicitly.
Before enabling it, disable every previous ARS Physics version for that savegame.
Keep exactly one ARS Physics package active to avoid applying physics changes twice.

## Validation scope
This beta was tested in a self-hosted multiplayer game using v0.1.18.7.
The game log confirms loading and initialization without ARS-specific Lua errors;
the operator accepted the driving behavior. This release preserves those physics
calculations with packaging, version and log-text corrections. No separate in-game
acceptance of v0.1.18.8, remote-client or dedicated-server test is claimed.

## Compatibility
Avoid enabling competing soil/tire-physics modifications simultaneously
(e.g. Soil Compaction, Longer Lasting Mud or Dirty Tire Tracks).
Advanced Damage System (ADS) may remain enabled for testing; this is not
a blanket compatibility guarantee for all versions or mod combinations.

## Feedback
- Discussion: https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/discussions/2
- Bug reports: https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/issues

## Rights
Author: KeilerHirsch. License: EUPL-1.2 (see LICENSE).
Based on GIANTS' native game interfaces, not copied source from other FS25 mods.

## Physics Beta 0.1.18.9 RC4 – deeper native visuals, lighter driving

**Built directly on native GIANTS physics.** This is a local test
candidate only. The last public Physics release remains 0.1.18.8.

Based on RC1's preferred vehicle handling. RC4 reduces only ARS'
additional rolling resistance on soil by 20% and on road to a
maximum of 1.2% (formerly 1.6%), and its active field-tool
draft increment by 20%. It does not manipulate native motor
torque or ADS heat. Heavy loads, steep hills and 38-degree heat
remain native/ADS effects; avoiding overheating is not guaranteed.

Visual deformable ground input: GIANTS WheelPhysics.displacementScale
scales up to 2.50x, with explicit profiles for plowed, cultivated,
seedbed, field, soft soil, firm ground, snow and non-deformable road.
Factors take wheel load, wheel width, wetness and crawler tracks
into account. Results depend on each map's native ground deformation.

Visible wheel sinking: native WheelPhysics.extraSinkSupported is
enabled when terrain deformation is supported, allowing GIANTS'
own updateSink to affect deltaY/real wheel pose. A per-wheel
extraSinkMaxValue target varies by surface/wheel load/width/
crawler/wetness: plowed ground normally up to ~0.16 m,
soft ground ~0.175 m, with a 0.20 m and 20%-of-radius safety cap.
Road target is zero. GIANTS MAX_SINK and interpolation still limit
the final result, so these are ceilings, not measured sink depths.

No manual wheel-mesh translation, no custom terrain height writes,
no new GUI/settings, no persistent rut journal. Prior per-wheel
native values are restored if ARS is disabled or unloaded.
Only one ARS Physics beta ZIP should be active. Backup test saves;
in-game results, log compatibility and multiplayer are unverified.