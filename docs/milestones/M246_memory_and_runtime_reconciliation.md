# ROBY M246 — Memory and Runtime Reconciliation

## Operational scope

M246 performs the first ordered architecture reconciliation over M245.

1. The historical memory adapter now writes through the official persistent
   personal-memory runtime and its configured `ROBY_PERSONAL_MEMORY_PATH`.
2. The five-turn recent buffer remains only as a compatibility view; it is no
   longer an independent source of persistent truth.
3. The empty legacy scheduler was removed from bootstrap, runtime lifecycle,
   and the historical proactive adapter.
4. `UnifiedCognitiveScheduler` and `HighLoadCognitiveScheduler` were preserved:
   they are active cognitive architecture components and are not the retired
   legacy scheduler.
5. The historical desktop builder is now an alias of the official unified
   desktop builder.
6. The definitive personal `.env` remains unchanged and included by design.

## Deferred integration inventory

The following families remain intentionally deferred to later ordered milestones:

- cognitive and episodic memory bridges;
- relationship and household memory projections;
- historical `core.roby.ROBY` compatibility retirement;
- capability reachability registry;
- optional retrieval and advanced runtime contributors.

They were not force-wired in M246 because each has its own contracts,
precedence rules, and persistence semantics.

## Certification

- Focused tests: 11 passed.
- Ruff: All checks passed.
- Full suite: 6050 passed.
- Skipped: 0.
- Regressions observed: 0.
