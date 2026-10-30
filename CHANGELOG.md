# Advanced Realism Suite — development changelog

> **Project status — 28 October 2026.** The standalone ARS Physics Beta is publicly available; the **full ARS suite remains unreleased**. Mainline development entries below describe work in progress, not shipped features.

## Prepared: ARS Physics Beta v0.1.18.9 — 30 October 2026

Native wheel sinking and ruts now respond more visibly to plowed soil, tyre width, wheel load, moisture and crawler setups. Narrow tyres can approach their physical rim-horn limit; wide tyres sink less. Improved native contact timing, terrain-collision guards and wheel-state restoration; engine torque unchanged. RC6 visuals and handling accepted in FS25, Lua 5.1 regression tests passed; no new MP/dedicated-server or ADS guarantee. [Short release notes](docs/RELEASE_NOTES_PHYSICS_0_1_18_9.md). This entry is **prepared**, not yet published.

## Released: ARS Physics Beta v0.1.18.8 — 28 October 2026

First standalone public module built on GIANTS-native vehicle physics. Includes terrain-dependent tire traction, wheel sinking influenced by soil, moisture, tires and load, rolling resistance and implement draft behavior. Self-hosted multiplayer gameplay was tested with the same physics in v0.1.18.7; dedicated servers and separate remote clients are not fully verified. Installation, compatibility and the exact package are documented in the [GitHub Releases section](https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/releases). This is **not** the full ARS suite.

## Unreleased: local 0.1.18.1 development candidates

**Development areas:** Unified P-Shop and paid workshop services; vehicle component condition and inspections; ARS Physics, Dirt, Exhaust and RealFuel; supported machinery and harvesting condition; engine tuning; used-equipment condition and resale calculations; save/stream and server-authority tests.

**Branding:** Product name corrected from Advanced Realms Suite to **Advanced Realism Suite (ARS)**; repository renamed to `FS25_Advanced_RealismSuite`. Historical GIANTS ZIP/package identity `FS25_Advanced_Realms_Suite` is retained until savegame/profile-key compatibility is verified.

**Still open:** Practical FS25 gameplay, UI, save/reload, multiplayer, dedicated-server and mixed-mod acceptance. Functional ADS 0.10.0.8-beta parity is still in progress. Automated build/test successes alone do not make features released.

See [Detailed feature status](docs/FEATURES.md), [Release notes template](docs/RELEASE_NOTES_TEMPLATE.md) and [GitHub Releases](https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/releases). Exact download checksums are provided with each published release.
