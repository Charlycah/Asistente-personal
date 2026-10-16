# M186 — Operational Runtime Consolidation

M186 consolidates the official M179-M185 execution path without adding cognitive authority.

## Delivered

- The console prompt is derived from the active bootstrap owner.
- `/tool` commands are forwarded to the governed runtime instead of being consumed by the UI.
- A daemon heartbeat supervisor maintains lifecycle availability while the console is idle.
- Supervisor start/stop is idempotent and never performs cognitive work.
- Abandoned leases may be recovered only when both the recorded PID is absent and the persisted heartbeat is stale.
- Active, recent, missing-state, or malformed leases fail closed.
- Memory and tool integration dependencies now use explicit runtime-checkable ports instead of `object`.
- Delivery hygiene removes bytecode, caches, Git metadata, local runtime state, and secrets.

## Architectural boundary

The console remains a thin adapter. The supervisor owns only lifecycle metadata. Tool execution still occurs exclusively through M184/M61. Lease recovery never overrides a live process.

## Deferred

Concrete provider wiring remains configuration-specific. The existing `ROBY_RUNTIME_ROOT_FACTORY` boundary is preserved until the next provider-adapter milestone supplies the selected local model runtime.
