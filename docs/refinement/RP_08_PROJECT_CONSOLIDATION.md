# RP.08 — Project Consolidation

RP.08 consolidates the ROBY project tree without changing runtime behavior.

## Changes

- Removed all committed Python bytecode and cache directories.
- Centralized refinement documentation under `docs/refinement/`.
- Added an explicit project-structure guide.
- Added a reusable local cleanup command.
- Preserved package-local tests where relocation would add risk without value.
- Kept the complete certification suite and all private household runtime data.

## Boundary

This refinement does not change cognition, memory, permissions, ambient
behavior, camera behavior, voice behavior or runtime composition.
