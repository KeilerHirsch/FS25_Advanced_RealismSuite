# ARS Physics Beta — v0.1.18.9

**More realism. All in one mod.**



**Mehr Realismus. Alles in einer Mod.**

Standalone physics preview for Farming Simulator 25, built directly on native GIANTS vehicle physics. This is the physics module only, not the complete ARS suite.

## English

### What's included
- **Deep, visible wheel sinking:** Freshly plowed and soft soil lets loaded tyres sink naturally toward the rim, without moving the wheel mesh independently.
- **Ground deformation:** Stronger native ruts with separate behavior for plowed, cultivated, seedbed, firm and wet ground. Paved roads stay largely unaffected.
- **Tyre-aware physics:** Wheel load, tyre width, moisture and crawler tracks influence sinking. Narrow tyres can sink deeper than wide tyres under comparable load.
- **Refined handling:** Terrain resistance and traction without exaggerated extra engine load. Native engine torque and gearbox remain unchanged.
- **Stability:** Corrected stopped-wheel return and native water-contact gating. Originally unsupported wheels are protected from extra water sinking; native behavior remains available for wheels that already supported it.

### Operator acceptance and compatibility
The operator tested the physics in FS25 on dry, freshly plowed soil, including narrow tractor tyres and wide, loaded Samson trailer tyres. The operator reported visually convincing sinking and balanced handling, confirmed the plowed-field-to-pavement stopping transition had been checked, and authorized publication. This is qualitative user acceptance; no measured sinking depth or repeatable telemetry is claimed.

Multiplayer support has not been verified for v0.1.18.9 and is declared unsupported in `modDesc.xml`. The earlier self-hosted multiplayer test covered v0.1.18.7 and does not establish support for this build. Dedicated servers and separate remote clients are also unverified. ADS thermal behavior and other mod interactions are not guaranteed.

### Install
Download the [v0.1.18.9 ZIP](https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/releases/download/v0.1.18.9-physics-beta/FS25_ARS_Physics_Beta_0_1_18_9.zip), put it in `FarmingSimulator2025/mods`, and enable it in the savegame. Disable every older ARS Physics version first; keep only one active. Back up your savegame. Avoid other mods that rewrite tyre or soil physics.

## Deutsch

### Enthaltene Funktionen
- **Deutlich tieferes Einsinken:** Schwere Räder tauchen auf lockerem Pflugacker sichtbar ein – bei passenden Reifen bis nahe ans Felgenhorn.
- **Natürlichere Fahrspuren:** Native Bodenverformung mit eigenem Verhalten für Pflugacker, bearbeiteten Boden, Saatbett, festen Untergrund und Feuchtigkeit. Befestigte Wege bleiben weitgehend unbeeinflusst.
- **Bereifung zählt:** Radlast, Reifenbreite, Feuchtigkeit und Raupenlaufwerke beeinflussen das Einsinken. Schmale Reifen sinken bei vergleichbarer Last stärker ein als breite.
- **Ausgewogenes Fahrgefühl:** Mehr spürbarer Widerstand und Traktion ohne überhöhte zusätzliche Motorlast. Motordrehmoment und Getriebe bleiben unverändert.
- **Stabilität:** Rückstellung stehender Räder und Wasser-Kontaktprüfung wurden korrigiert. Ursprünglich nicht sinkfähige Räder erhalten kein zusätzliches Wassereinsinken; natives Verhalten bleibt für entsprechend konfigurierte Räder erhalten.

### Nutzerabnahme und Kompatibilität
Der Operator testete die Physik in FS25 auf trockenem, frisch gepflügtem Boden, darunter schmale Traktorreifen sowie breite, beladene Samson-Anhängerreifen. Er beschrieb das Einsinken als optisch überzeugend und das Fahrverhalten als ausgewogen, bestätigte den bereits geprüften Übergang vom Pflugacker auf den befestigten Weg samt Anhalten und erteilte die Freigabe zur Veröffentlichung. Das ist eine qualitative Nutzerabnahme; es werden keine gemessene Einsinktiefe oder reproduzierbare Telemetrie behauptet.

Multiplayer-Unterstützung ist für v0.1.18.9 nicht verifiziert und in `modDesc.xml` als nicht unterstützt deklariert. Der frühere Test im selbst gehosteten Multiplayer bezog sich auf v0.1.18.7 und belegt diese Version nicht. Dedicated Server und getrennte Remote-Clients sind ebenfalls unverifiziert. ADS-Temperaturverhalten und Wechselwirkungen mit anderen Mods sind nicht garantiert.

### Installation
Die [ZIP-Version 0.1.18.9](https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/releases/download/v0.1.18.9-physics-beta/FS25_ARS_Physics_Beta_0_1_18_9.zip) in den Ordner `FarmingSimulator2025/mods` legen und im Spielstand aktivieren. Alle älteren ARS-Physics-Versionen vorher deaktivieren; nur eine Version aktiv lassen. Spielstand sichern und keine anderen Reifen-/Bodenphysik-Mods parallel nutzen.

## Links

- [Release notes / Versionshinweise](https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/blob/v0.1.18.9-physics-beta/docs/RELEASE_NOTES_PHYSICS_0_1_18_9.md)
- [GitHub release / GitHub-Veröffentlichung](https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/releases/tag/v0.1.18.9-physics-beta)
- [Discussion](https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/discussions/2) · [Bug reports](https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/issues)

**Author:** KeilerHirsch · **License:** EUPL-1.2 (see `LICENSE`). Project-controlled code is original and uses GIANTS engine interfaces.
