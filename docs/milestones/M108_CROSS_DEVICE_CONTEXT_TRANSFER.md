# M108 — Cross-Device Context Transfer

M108 introduces a governed preparation layer for transferring selected session context from one verified device to another.

## Scope

- immutable transferable context fragment descriptors;
- ownership and session coherence validation;
- integration with M106 continuity decisions;
- integration with M107 capability matches;
- sensitivity, expiry and capability filtering;
- partial-transfer manifests;
- deterministic integrity digests;
- auditable in-memory repository.

## Explicit non-goals

M108 does not transport bytes, copy messages, synchronize memory, move credentials, open network connections, mutate sessions, select the active device or implement Mobile Companion.

## Quality gate

- Ruff clean;
- 38 focused M108 tests;
- full repository suite passing without regressions.
