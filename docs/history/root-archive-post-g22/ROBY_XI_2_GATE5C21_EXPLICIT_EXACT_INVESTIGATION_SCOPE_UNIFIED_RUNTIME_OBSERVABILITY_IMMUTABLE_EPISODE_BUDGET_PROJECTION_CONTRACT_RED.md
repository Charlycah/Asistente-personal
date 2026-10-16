# ROBY XI.2 — GATE 5.C.2.1 — CONTRACT RED

## Explicit Exact Investigation Scope → UnifiedRuntimeObservability Immutable Episode/Budget Projection

### Certified entry

GATE 5.C.2 ARCHITECTURAL RECONCILIATION is the certified entry baseline:
**14,043 PASS · Ruff clean · 0 FAIL**.

This gate is CONTRACT RED only. Production remains byte-identical to the
certified GATE 5.C.2 baseline.

## Architectural purpose

Freeze the smallest legitimate publication seam from the already-certified
owner-level exact-scope investigation episode/budget introspection into
`UnifiedRuntimeObservability`.

Canonical chain:

`explicit exact scope`
→ `UnifiedRuntimeObservability`
→ `runtime.root.dependencies.governed_reasoning_runtime`
→ `investigation_episode_budget_introspection(...)`
→ immutable episode/budget projection.

## Frozen contract

1. `UnifiedRuntimeObservability` accepts one explicit exact investigation scope.
2. Scope is an immutable value object only, not a manager/registry/authority.
3. Scope contains exactly `owner`, `session_id`, and `turn_id`.
4. No scope means no episode selection and projection is `None`.
5. No reasoning runtime provisioned means projection is `None`.
6. Missing exact canonical episode means projection is `None`.
7. Present exact scope delegates once to the canonical governed reasoning owner.
8. The unified snapshot publishes the exact frozen owner-level view returned by
   `investigation_episode_budget_introspection(...)`; it does not reconstruct it.
9. Unified observability must not read private reasoning stores.
10. No latest-episode inference, global budget, active-episode scan or
    cross-domain episode fusion.
11. No Reasoning, Planning, Authorization, Execution, Reflection, Memory or
    Learning execution is opened by this projection.
12. No new manager, registry, graph, runtime, authority or persistence.
13. `OfficialConversationGateway` / Analysis Mode remain byte-identical and out
    of scope.
14. `OfficialGovernedReasoningRuntimeGateway` remains byte-identical; GATE 5.C.1
    is reused, not rewritten.
15. G5-R3d versions remains STOP.
16. G5-R3e certifications/quality remains STOP.
17. G5-R4 remains STOP.
18. `.roby/config.json` remains byte-identical.

## RED public names

The RED freezes these names for the future surgical GREEN:

- `InvestigationEpisodeBudgetObservabilityScope`
- `investigation_scope=` on `UnifiedRuntimeObservability.snapshot(...)`
- `UnifiedRuntimeObservabilitySnapshot.investigation_episode_budget`

## Expected RED

Only the missing UnifiedRuntimeObservability scope/projection seam should fail.
Existing owner-level GATE 5.C.1 behavior and all lateral architecture guards
must remain GREEN.

## STOP

Analysis Mode TECHNICAL is not part of this gate. Publication into conversation
must not be added automatically after this RED or its future GREEN.
