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

## Physics Beta v0.1.18.9 release candidate (not published)

The previous public release is v0.1.18.8. This is the next patch version
(v0.1.18.9), regardless of the higher local DEV iteration numbers used during
tuning. There is no GitHub push or release for this candidate yet.

Built directly on the native GIANTS physics routines. The stock motor torque
curve remains unchanged (1.00x); rolling, traction, and implement draft follow
the operator-approved prior calibration. Road/hard rolling damping continues
to respond *very slightly* to wheel load and wetness (no trailer-class tax).
The only physics change since local DEV 0.1.18.11 is an additional boost to
native sinking targets across non-road terrain profiles. Even on hard or
uncategorized surfaces, an ARS sinking multiplier is applied only where the
GIANTS WheelPhysics.MAX_SINK base value is positive. Asphalt stays 1.00x,
and GIANTS still owns sinking interpolation and ground geometry.

This last sink-only adjustment is awaiting in-game acceptance. Keep only one
Physics Beta ZIP active at a time. Savegame backups are recommended.