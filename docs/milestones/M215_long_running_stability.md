# M215 — Long-Running Stability

M215 adds bounded stability supervision for extended ROBY sessions.

## Capabilities

- Per-owner and per-session cycle tracking.
- Bounded observation history with configurable retention.
- Deterministic drift scoring between consecutive cognitive schedules.
- Stability states: `stable`, `observing`, `checkpoint_required`, and `guarded`.
- Directives: `continue`, `observe`, `checkpoint`, and `stabilize`.
- Periodic checkpoint policy without checkpoint execution authority.
- Blackboard publication and complete source lineage.
- Official placement immediately after M214.

## Architectural boundary

M215 observes and recommends. It does not recover components, restart providers,
execute tools, manage operating-system resources, or introduce parallel workers.
Recovery remains in M213, high-load admission remains in M214, and concurrent
execution is reserved for M216.

## Validation

- Focused M215 tests: 15 passed.
- Ruff: all checks passed.
- Full suite: 5,499 passed.
- Regressions: zero.
