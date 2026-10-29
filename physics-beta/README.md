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

## Physics tuning development candidate 0.1.18.10
This development candidate keeps the native GIANTS motor torque curve unchanged (1.00x), removes the extra trailer-class rolling tax, and retunes soil sinking with a 2.35x sink-target cap. Operator feedback on the 0.1.18.9 tuning was positive. This candidate additionally applies a tiny 0-1.6% rolling-damping adjustment on road/hard ground according to actual per-wheel load and current ground wetness. Normal GIANTS mass, fill weights, slope forces, and wet tire friction remain authoritative. This 0.1.18.10 road refinement has not yet been field-tested; the published release is still 0.1.18.8.
