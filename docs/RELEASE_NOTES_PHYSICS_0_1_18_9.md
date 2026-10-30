# ARS Physics Beta — v0.1.18.9

**More realism. All in one mod.**
Standalone physics preview for Farming Simulator 25 — built directly on native GIANTS physics.

## What's new
- **Deep, visible wheel sinking:** Freshly plowed and soft soil lets loaded tyres sink naturally toward the rim, without moving the wheel mesh independently.
- **Ground deformation:** Stronger native ruts with separate behavior for plowed, cultivated, seedbed, firm and wet ground. Paved roads stay largely unaffected.
- **Tyre-aware physics:** Wheel load, tyre width, moisture and crawler tracks influence sinking. Narrow tyres can sink deeper than wide tyres under comparable load.
- **Refined handling:** Noticeable off-road resistance and traction without exaggerated extra engine load. Native engine torque and gearbox remain unchanged.
- **Stability improvements:** Better native wheel-contact timing, terrain-collision guards, state restoration and fewer repeated wheel-load calculations.

**Installation:** Replace the previous ARS Physics Beta ZIP; enable only **one** ARS Physics version per savegame. Back up your savegame. Avoid other mods that rewrite tyre/soil physics.

**Beta status:** Qualitative in-game screenshots and driving feedback on dry plowed soil; no instrumented sinking-depth test. Local Lua 5.1 smoke tests pass. Dedicated-server and independent multiplayer-client compatibility are not yet verified. ADS thermal behavior is not guaranteed.

**This is the standalone Physics Beta, not the complete Advanced Realism Suite.**

[Feedback](https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/discussions/2) · [Report a bug](https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/issues)

---

## Deutsch

**Mehr Realismus. Alles in einer Mod.** Eigenständige Physics Beta für LS25 – direkt auf der nativen GIANTS-Physik aufgebaut.

### Neuerungen
- **Deutlich tieferes Einsinken:** Schwere Räder tauchen auf lockerem Pflugacker sichtbar ein – bei passenden Reifen bis nahe ans Felgenhorn.
- **Natürlichere Fahrspuren:** Native Bodenverformung, abgestimmt auf Bearbeitung, Feuchtigkeit und Radlast.
- **Bereifung zählt:** Schmale Reifen, Breitreifen und Raupen reagieren unterschiedlich; auch Zuladung und Reifenbreite fließen ein.
- **Besser abgestimmtes Fahrgefühl:** Mehr spürbare Bodenphysik ohne unnötige Änderungen an Motordrehmoment oder Getriebe.
- **Technische Verbesserungen:** GIANTS-Radlast, Kontaktaktualisierung, Kollisionsprüfung und saubere Rückstellung.

**Installation:** Alte ARS-Physics-Version deaktivieren, nur **eine** ZIP aktivieren. Spielstand vorher sichern. Andere Reifen-/Bodenphysik-Mods möglichst nicht parallel nutzen.

**Beta-Hinweis:** Screenshots und Fahrfeedback vom Operator auf trockenem Pflugacker; keine instrumentierte Einsinktiefenmessung. Lokale Lua-Tests bestanden. Dedicated Server und getrennte MP-Clients noch nicht nachgewiesen; ADS-Temperaturverhalten nicht garantiert.

**Nicht die vollständige ARS-Suite.**


### Test evidence and operator sign-off (2026-10-30)
The operator reviewed RC6 in Farming Simulator 25 on dry, freshly plowed soil, including narrow tractor tyres and wide loaded Samson trailer tyres, and reported visually convincing wheel sinking and balanced handling. After being asked to check the plowed-field-to-pavement stopping transition, the operator explicitly replied that this test had already been performed and authorized publication. These are operator statements, not instrumented logs, controlled measurements or an independent verification of the exact packaged SHA-256. The final package also contains the small native stopped-wheel return correction, verified by a targeted Lua 5.1 regression matching GIANTS updateSink's assignment behavior. No remote multiplayer/dedicated server or ADS thermal guarantee is made. This is an experimental beta release.
**Release package:** FS25_ARS_Physics_Beta_0_1_18_9.zip
**SHA-256:** EB908EB261A5BC59024BD6E5FBDFE2DCA44BC827D5B29B3778AD1C1BC04F8D16
