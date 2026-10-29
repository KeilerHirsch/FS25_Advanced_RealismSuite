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

## Physics Beta v0.1.18.9 RC3 / native terrain visual test

**Built directly on native GIANTS physics.** No separate physics engine,
visual wheel teleportation, or artificial motor torque boost. Public version
remains 0.1.18.9 (the next patch after published 0.1.18.8).

Operator-driven rollback: restore all soil, sinking, road, grip, rolling,
draft and motor values from the previously liked RC1. The heavy-load
overheating observed on RC2 is not yet established as ARS-caused and is
not claimed fixed.

Only new behavior: on server wheels that permit GIANTS wheel terrain
displacement, use GIANTS' own WheelPhysics.displacementScale and
setDisplacementAllowed() to drive native terrain deformation/ruts at a
factor between 1.00x and 1.50x of the existing vehicle wheel baseline.
Relative gain varies with native soil / cultivation state, contact wheel
load (including fill mass when GIANTS exposes it), tire footprint,
crawler type and ground wetness. Road remains 1.00x and the original
displacement scale is restored when terrain stops deforming or the
physics module is disabled. The game engine still owns geometry,
ground contact, wheel visuals and persistence. 1.50x is a native
displacement input, NOT a guarantee of 50% more visible centimeters
or additional physical wheel sink. No terrain editing APIs or data
persistence are added.

**Testing status:** isolated Lua smoke tests and packaging tests only.
The in-game visual result and multiplayer behavior need operator
confirmation before publication. Do not activate concurrently with
other mods that overwrite GIANTS wheel terrain displacement.