# Contributor and agent guidance

**Project:** Advanced Realism Suite (ARS), an independent Farming Simulator 25 realism and immersion mod.
**Licence for project-controlled code:** EUPL-1.2.

These guidelines apply to contributions and automated changes in this repository.

## Principles

- Work from existing code and confirmed GIANTS FS25 interfaces before adding custom hooks.
- Treat physics, engine load, fuel use, machinery condition and repairs as connected systems; avoid competing state owners.
- Preserve game stability, savegame compatibility, multiplayer/server authority and reasonable mod interoperability.
- Write original ARS code. Do not copy or adapt source code from other mods without verified licence compatibility and authorization.
- Do not import third-party graphics, sounds, models or other assets without valid rights and notices.
- Do not commit credentials, personal data, game saves, private logs or machine-specific files.
- Keep public claims bounded by actual builds and test results. Never present planned systems as released.
- Prefer focused changes, justified dependencies and verifiable gameplay paths over broad rewrites.
- Test Lua/XML/build paths as applicable, and distinguish automated checks from real in-game, save/reload and multiplayer acceptance.
- Keep contributions reviewable and provide relevant verification evidence.

## Review lens

A complete gameplay change should connect: **operating conditions → machine state → player-visible effect → diagnosis/maintenance → saved and synchronized result**.

Follow [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).
