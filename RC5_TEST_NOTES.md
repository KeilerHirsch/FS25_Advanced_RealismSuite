ARS Physics Beta 0.1.18.9 RC5 SINK50 - Test notes 29 October 2026
Calibrated physical native plowed sink at 1.50x Vanilla dry/reference load.
Other surface/load/wetness/crawler adjustments are bounded at 1.95x.
Real sink is still limited by native MAX_SINK, contact, native speed gate,
and 0.20 metres/20 percent of tyre radius. No in-game depth claim yet.
Actual native sink feeds mild rut coordination, not nominal cap alone.
Native getTireLoad is preferred with fallback and per-wheel frame cache.
Field-state tables are static. Contact-aware cap is set within updateSink.
No permanent global MAX_SINK changes. Respect terrain collision flag.
Smooth parked road sink restore and map-unload cleanup.
Original vehicle-specific extraSink configuration remains intact.
Motor torque and gears are vanilla, drag/draft same as RC4.
Close LS25 before swapping ZIP. One active ARS Physics only.
No public push, no main-worktree edits. Tests are offline simulation only.