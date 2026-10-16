# M179 — Local Runtime Bootstrap

## Objective

Create ROBY's official local process bootstrap over the M178 runtime composition root.

## Bootstrap path

1. Load explicit owner, session, state path, and runtime-root factory configuration.
2. Obtain one configured `RuntimeCompositionRoot` from the injected factory.
3. Compose the official M178 graph exactly once.
4. Persist immutable lifecycle metadata atomically.
5. Keep the process alive until an explicit shutdown signal.
6. Stop idempotently while preserving the original start timestamp.

## Governance

- M179 owns process lifecycle only.
- It does not classify input, prepare turns, call providers, retrieve knowledge, assemble responses, or mutate the platform.
- Runtime dependency construction remains explicit through `ROBY_RUNTIME_ROOT_FACTORY=module:function`.
- Persisted state contains only owner, session, lifecycle status, timestamps, and failure detail.
- No conversation content or cognitive state is persisted by this milestone.
- Persisted owner and session identity cannot be silently reused by another identity.
- State writes use a temporary file followed by atomic replacement.

## Delivered

- `LocalRuntimeBootstrapConfig`, `LocalRuntimeState`, and `LocalRuntimeStatus`.
- `LocalRuntimeBootstrap` with idempotent `start()` and `stop()`.
- JSON lifecycle state store with atomic local writes.
- Restart-state loading and identity validation.
- Explicit environment-driven root factory loader.
- Official root-level `main.py` with SIGINT/SIGTERM shutdown handling.

## Validation

- 20 focused M179 tests.
- 40 combined M178-M179 tests.
- Ruff clean.
- 5011 repository tests passing without regressions.
