# ARS Physics Beta — v0.1.18.9

**Advanced Realism Suite (ARS)** — an independent Farming Simulator 25 physics preview.
**More realism. All in one mod.** Built directly on native GIANTS physics, not a second physics engine.

## Features
- **Native wheel sinking:** Deeper wheel penetration on loose/plowed ground, capped by physical wheel and rim geometry.
- **Native terrain deformation:** Stronger, soil-specific wheel ruts.
- **Real tyre/load response:** Narrow/wide tyres, vehicle weight, moisture, cultivation state and crawler tracks affect sinking.
- **Balanced driving:** Terrain-dependent grip, rolling resistance and working-tool draft. Original GIANTS engine torque, gearbox and horsepower remain unchanged.
- **Stability:** Original wheel-state restoration, terrain-collision guards, native contact timing and efficient wheel-load lookups.

## Installation
1. Download **FS25_ARS_Physics_Beta_0_1_18_9.zip** from the matching GitHub release.
2. Put the ZIP in your `FarmingSimulator2025/mods` folder and explicitly enable the new version in your savegame.
3. **Disable all older ARS Physics versions** before loading the save; only one should be active.
4. Back up your save before updating.

## Compatibility and test scope
The operator supplied screenshots of dry plowed terrain with narrow tractor tyres and loaded trailer tyres, plus qualitative driving feedback; this is not a measured in-game benchmark. Local Lua 5.1 smoke tests pass. A previous Physics Beta (v0.1.18.7) was used in self-hosted multiplayer; **dedicated server and independent remote-client behavior are not yet validated for v0.1.18.9**.

ADS may remain enabled for testing, but overheating and other mod interactions are not guaranteed. Avoid competing tyre/soil physics modifications while comparing results. This beta does **not** include the complete ARS suite or a new mud/dirt visual effects system.

## Feedback and rights
[Discussion](https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/discussions/2) · [Bug reports](https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/issues) · [Release notes](https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/blob/main/docs/RELEASE_NOTES_PHYSICS_0_1_18_9.md)

**Author:** KeilerHirsch · **License:** EUPL-1.2 (see LICENSE). Project-controlled code is original, using GIANTS engine interfaces.
