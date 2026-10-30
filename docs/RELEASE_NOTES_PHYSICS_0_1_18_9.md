# ARS Physics Beta — v0.1.18.9

**More realism. All in one mod.**



**Mehr Realismus. Alles in einer Mod.**

Standalone Farming Simulator 25 physics beta built directly on native GIANTS vehicle physics. This release is the physics module only, not the complete ARS suite.

## English

### What's new
- **Deep, visible wheel sinking:** Freshly plowed and soft soil lets loaded tyres sink naturally toward the rim, without moving the wheel mesh independently.
- **Ground deformation:** Stronger native ruts with separate behavior for plowed, cultivated, seedbed, firm and wet ground. Paved roads stay largely unaffected.
- **Tyre-aware physics:** Wheel load, tyre width, moisture and crawler tracks influence sinking. Narrow tyres can sink deeper than wide tyres under comparable load.
- **Refined handling:** More noticeable off-road resistance and traction without exaggerated extra engine load. Native engine torque and gearbox remain unchanged.
- **Stability:** Corrected native stopped-wheel return and water-contact gating. Wheels that did not originally support native extra sinking no longer receive water sinking from ARS; GIANTS water behavior remains available to wheels that already supported it.

### Operator acceptance and test scope
The operator tested the physics in Farming Simulator 25 on dry, freshly plowed soil, including narrow tractor tyres and wide, loaded Samson trailer tyres. The operator reported visually convincing sinking and balanced handling, confirmed the plowed-field-to-pavement stopping transition had been checked, and authorized publication. This is qualitative user acceptance; no measured sinking depth or repeatable telemetry is claimed.

The GIANTS multiplayer declaration remains enabled (`<multiplayer supported="true"/>`). Self-hosted multiplayer was tested with the same core physics in v0.1.18.7; that historical test does not verify all v0.1.18.9 changes. Dedicated servers and separate remote clients were not tested for this build. This incomplete multiplayer coverage is an accepted beta limitation. Local Lua 5.1 regression tests pass. ADS thermal behavior and other mod interactions are not guaranteed.

### Installation
Replace the previous ARS Physics Beta ZIP and enable only one ARS Physics version per savegame. Back up the savegame first. Avoid other mods that rewrite tyre or soil physics.

## Deutsch

### Neuerungen
- **Deutlich tieferes Einsinken:** Schwere Räder tauchen auf lockerem Pflugacker sichtbar ein – bei passenden Reifen bis nahe ans Felgenhorn.
- **Natürlichere Fahrspuren:** Native Bodenverformung mit eigenem Verhalten für Pflugacker, bearbeiteten Boden, Saatbett, festen Untergrund und Feuchtigkeit. Befestigte Wege bleiben weitgehend unbeeinflusst.
- **Bereifung zählt:** Radlast, Reifenbreite, Feuchtigkeit und Raupenlaufwerke beeinflussen das Einsinken. Schmale Reifen sinken bei vergleichbarer Last stärker ein als breite.
- **Ausgewogenes Fahrgefühl:** Mehr spürbarer Widerstand und Traktion abseits befestigter Wege ohne überhöhte zusätzliche Motorlast. Motordrehmoment und Getriebe bleiben unverändert.
- **Stabilität:** Rückstellung stehender Räder und die Wasser-Kontaktprüfung für natives Einsinken wurden korrigiert. ARS lässt ursprünglich nicht sinkfähige Räder bei Wasserkontakt nicht zusätzlich einsinken; das native GIANTS-Verhalten bleibt für bereits dafür konfigurierte Räder erhalten.

### Nutzerabnahme und Testumfang
Der Operator testete die Physik in Farming Simulator 25 auf trockenem, frisch gepflügtem Boden, darunter schmale Traktorreifen sowie breite, beladene Samson-Anhängerreifen. Er beschrieb das Einsinken als optisch überzeugend und das Fahrverhalten als ausgewogen, bestätigte den bereits geprüften Übergang vom Pflugacker auf den befestigten Weg samt Anhalten und erteilte die Freigabe zur Veröffentlichung. Das ist eine qualitative Nutzerabnahme; es werden keine gemessene Einsinktiefe oder reproduzierbare Telemetrie behauptet.

Die GIANTS-Multiplayerdeklaration bleibt aktiviert (`<multiplayer supported="true"/>`). Selbst gehosteter Multiplayer wurde mit derselben Kernphysik in v0.1.18.7 getestet; dieser frühere Test verifiziert nicht alle Änderungen von v0.1.18.9. Dedicated Server und getrennte Remote-Clients wurden für diesen Build nicht getestet. Diese unvollständige MP-Abdeckung ist eine akzeptierte Beta-Einschränkung. Lokale Lua-5.1-Regressionstests sind bestanden. ADS-Temperaturverhalten und Wechselwirkungen mit anderen Mods sind nicht garantiert.

### Installation
Die bisherige ARS-Physics-Beta-ZIP ersetzen und pro Spielstand nur eine ARS-Physics-Version aktivieren. Vorher den Spielstand sichern. Keine anderen Mods parallel nutzen, die Reifen- oder Bodenphysik verändern.

## Release

- **Version:** 0.1.18.9
- **Download:** [FS25_ARS_Physics_Beta_0_1_18_9.zip](https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/releases/download/v0.1.18.9-physics-beta/FS25_ARS_Physics_Beta_0_1_18_9.zip)
- **Release page:** [ARS Physics Beta v0.1.18.9](https://github.com/KeilerHirsch/FS25_Advanced_RealismSuite/releases/tag/v0.1.18.9-physics-beta)
- **SHA-256:** AB724DD8998F05AE064B6874FC8911DB91C2020167EC9728052642988CA14A6E
