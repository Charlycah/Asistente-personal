# ROBY XI.2 — INTEL-G2 — CONTRACT RED

## Durable Learning Temporal Read-Only Introspection

Baseline: 14.063 PASS · Ruff clean · 0 FAIL (user-certified source baseline).

This RED adds contract tests only. Production code is unchanged.

The contract freezes five missing obligations:

1. `CognitiveMemorySearch` exposes explicit `created_at_from` and `created_at_before` bounds.
2. `CognitiveMemoryStore.search` supports a half-open temporal interval while retaining the canonical `governed_learning` tag filter.
3. `MemoryRuntimeIntegration` exposes owner-scoped `governed_learning_temporal_introspection`.
4. `OfficialMemoryGateway` exposes the same official read-only introspection seam.
5. The official projection is represented by a frozen `GovernedLearningTemporalIntrospectionView`.

Semantics frozen by reconciliation:

- exact owner comes from `OfficialMemoryGateway`;
- temporal bounds are explicit; Memory does not interpret “today”;
- interval semantics are `[created_at_from, created_at_before)`;
- only canonical `governed_learning` records qualify;
- result remains bounded;
- introspection must be read-only and must not mutate access counters;
- no new store, ledger, registry, Learning authority, Knowledge authority or Memory authority;
- no direct SQL from Conversation/Analysis;
- no Library/Internet/Learning execution;
- no INTEL-G2.1 conversational projection yet.

Expected RED state: exactly five intentional failures in the new contract test file against unchanged production.
