# ROBY XI.2 — GATE 5.C.1 — CONTRACT RED

## Official Governed Reasoning Runtime Canonical Investigation Episode/Budget State → Scoped Immutable Read-Only Introspection View

### Base de entrada

- GATE 5.C architectural reconciliation: certified and closed by the user.
- Productive baseline: 14.034 PASS, Ruff clean, 0 FAIL.
- `app/governed_reasoning_runtime.py` protected entry SHA-256:
  `488ad061f846d3929957c19e1bb745b4d2bf4896ef413c1cab256d66092f87a0`.

## Scope frozen by this RED

This contract opens only the owner-level seam identified by GATE 5.C:

`OfficialGovernedReasoningRuntimeGateway`
→ exact owner/session/turn scope
→ immutable read-only investigation episode/budget view.

It does not publish the view to `UnifiedRuntimeObservability` or Analysis Mode.

### Required semantics

1. Source authority remains `OfficialGovernedReasoningRuntimeGateway`.
2. Exact `owner`, `session_id`, and `turn_id` scope is mandatory.
3. Missing exact scope returns honest absence (`None`), never a synthetic episode.
4. The public view is immutable/frozen.
5. The view preserves canonical episode and lineage fields:
   episode/reasoning/source/world snapshot/requirements/plans/authorizations/
   executions/local executions/reentries.
6. Budget semantics are copied from canonical episode state:
   `consumed_acquisitions`, `max_acquisitions`, `remaining_acquisitions`,
   `current_step`, status and stopping reason.
7. No global budget is calculated.
8. No `EpisodeRegistry`, `BudgetManager`, second runtime, or parallel authority.
9. No direct public exposure of private stores.
10. No fusion with epistemic/concept/abstraction/long-horizon stores.
11. Introspection must not execute Reasoning, Planning, Authorization, Execution,
    Reflection, Memory or Learning.
12. `UnifiedRuntimeObservability` and Analysis Mode remain unchanged in this gate.
13. G5-R3d versions, G5-R3e certifications/quality and G5-R4 remain STOP.
14. `.roby/config.json` remains unchanged.

### RED expectation

The certified baseline does not yet expose
`investigation_episode_budget_introspection(...)` nor the immutable public
read-model type. Therefore the new contract must fail only on that missing
owner-level seam while historical tests remain green.

No productive code is modified in CONTRACT RED.
