# ADR-181 — Local Runtime Bootstrap

## Status
Accepted

## Context
M178 defines ROBY's single governed composition root, but a composition graph alone does not provide a durable local process boundary. ROBY needs one explicit bootstrap that can be launched from the laptop, preserve operational identity across restarts, expose lifecycle state, and shut down predictably without moving cognitive decisions into the entrypoint.

## Decision
Introduce `core.local_runtime_bootstrap` as the official local process lifecycle boundary.

- The bootstrap receives an already configured `RuntimeCompositionRoot`.
- `start()` composes M178 exactly once and performs no conversation, inference, retrieval, network access, or platform mutation.
- Owner and session identity are explicit and must match any persisted lifecycle state.
- Lifecycle metadata is written atomically to a local JSON file.
- Persisted state contains no conversation text, prompts, responses, memories, or provider payloads.
- Start and stop are idempotent.
- Failures are recorded explicitly when possible and are re-raised to the caller.
- `main.py` loads the root through an explicit `module:function` factory configured in `ROBY_RUNTIME_ROOT_FACTORY`, then remains active until SIGINT or SIGTERM.

## Consequences
ROBY now has a single long-running local bootstrap compatible with VS Code and terminal execution. Concrete dependency construction remains outside the lifecycle boundary, cognitive work remains in governed runtime modules, and M180 can add the first end-to-end conversation loop without redefining startup semantics.
