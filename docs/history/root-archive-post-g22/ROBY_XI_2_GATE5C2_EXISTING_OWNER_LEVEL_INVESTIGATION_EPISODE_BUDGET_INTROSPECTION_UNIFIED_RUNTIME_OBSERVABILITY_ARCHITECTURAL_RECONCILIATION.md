# ROBY XI.2 — GATE 5.C.2 — ARCHITECTURAL RECONCILIATION

## Existing Owner-Level Investigation Episode/Budget Introspection → UnifiedRuntimeObservability

### Certified entry

Source: GATE 5.C.1 SURGICAL GREEN.
Source ZIP SHA-256: `4ef3bb622118ae0a3bf44a429011569946accd332f09e413e67e3f227bba3cff`.
User certification: **14,043 PASS · Ruff clean · 0 FAIL**.

This gate is reconciliation only. No productive code is modified.

## Governing rule

One ROBY, one governed brain, one canonical authority per capability.
Do not create a second episode registry, budget manager, runtime, graph,
manager, store, or inferred global episode view.

## Existing certified owner-level seam

`OfficialGovernedReasoningRuntimeGateway` already exposes:

`investigation_episode_budget_introspection(owner, session_id, turn_id)`

and returns frozen:

`GovernedInvestigationEpisodeBudgetIntrospectionView | None`.

The view is exact-scope and preserves the canonical retained investigation
episode state and bounded acquisition budget. Missing exact scope returns
`None`.

## Existing runtime reachability

`RuntimeCompositionDependencies` already contains:

`governed_reasoning_runtime: object | None = None`

and the productive runtime factory constructs one
`OfficialGovernedReasoningRuntimeGateway` and passes that same instance into
runtime composition.

Therefore UnifiedRuntimeObservability can already reach the canonical owner
through:

`runtime.root.dependencies.governed_reasoning_runtime`

No new runtime wiring or authority is required.

## Existing UnifiedRuntimeObservability boundary

`UnifiedRuntimeObservability.snapshot(...)` currently accepts runtime plus
recovery-oriented `graph`, `capabilities`, and `now`.

Its frozen snapshot already publishes operational/readiness/conversation,
capability registry/dependencies, cognitive core, self model, reflection,
self-diagnostics availability, and recovery.

It does **not** currently publish investigation episode/budget state and does
not read `governed_reasoning_runtime`.

## Critical scope finding

The new owner-level seam deliberately requires all three exact identifiers:

- `owner`
- `session_id`
- `turn_id`

UnifiedRuntimeObservability does not currently possess that exact scope.

`OfficialConversationGatewaySnapshot` exposes `last_session_id`, but it does
not expose owner or turn_id. Therefore it is architecturally invalid for
UnifiedRuntimeObservability to infer the requested investigation scope from
conversation state.

It is also invalid to:

- choose the "latest" reasoning/investigation episode;
- scan `_productive_explanatory_investigation_reentries`;
- reconstruct owner/session/turn from registry, imports, filenames or wiring;
- synthesize a global active-episode or global-budget view;
- merge unrelated epistemic/concept/abstraction/long-horizon stores.

## Reconciliation classification

**CANONICAL OWNER EXISTS + OFFICIAL RUNTIME REACHABILITY EXISTS + CERTIFIED
EXACT-SCOPE IMMUTABLE VIEW EXISTS + UNIFIED OBSERVABILITY LACKS AN EXPLICIT
EXACT-SCOPE QUERY INPUT AND SNAPSHOT PROJECTION.**

The residual is no longer owner-level storage or runtime wiring.

The residual is a narrow read-only publication seam:

`caller-supplied exact owner/session/turn scope`
→ `UnifiedRuntimeObservability`
→ `runtime.root.dependencies.governed_reasoning_runtime`
→ `investigation_episode_budget_introspection(...)`
→ immutable snapshot projection.

## Recommended CONTRACT RED for GATE 5.C.2.1

Freeze only this publication contract:

1. UnifiedRuntimeObservability may accept explicit exact investigation scope.
2. Scope must preserve owner + session_id + turn_id exactly; no inference.
3. If no exact scope is supplied, investigation projection is `None`.
4. If reasoning runtime is not provisioned, projection is `None`.
5. If exact scope has no canonical retained episode, projection is `None`.
6. If present, the snapshot publishes the exact frozen owner-level view
   returned by `investigation_episode_budget_introspection(...)`.
7. UnifiedRuntimeObservability must not read any private reasoning store.
8. UnifiedRuntimeObservability must not call productive Reasoning, Planning,
   Authorization, Execution, Reflection, Memory or Learning.
9. No global budget, latest-episode selection, store scan or cross-domain merge.
10. No new manager, registry, graph, runtime, authority or persistence.
11. Analysis Mode remains unchanged and out of scope.
12. G5-R3d versions remains STOP.
13. G5-R3e certifications/quality remains STOP.
14. G5-R4 remains STOP.
15. `.roby/config.json` remains byte-identical.

### Design note

The scope should be query input, not runtime state. This preserves the
certified exact-scope semantics of GATE 5.C.1 and prevents observability from
inventing a current episode.

The RED should decide the smallest public shape for that query input
(preferably explicit owner/session_id/turn_id parameters or one immutable
value object), but must not create a manager/registry/authority.

## Explicit non-goals

- No Analysis Mode TECHNICAL projection yet.
- No active episode inventory.
- No global episode/budget snapshot.
- No later-transition synthesis.
- No diagnostics execution.
- No repository/test/Ruff scans from ROBY.
- No Memory/Learning.
- No Planning N+1.
- No G5-R4.

## Protected source hashes at reconciliation

- `app/governed_reasoning_runtime.py`: `26a9f4f6c1fb629f857f5b2943b9d80a56edc641ba38a730e900317704e008ba`
- `app/unified_runtime_observability.py`: `fca88a4cea7c8649213f3f09a099adde2db3abfc394396f6f0ee6ea6d02ef535`
- `app/official_conversation_gateway.py`: `737ba00cb82cf58dd890876996af52d74b9efad57e11641ebb5918671567b9c9`
- `core/runtime_composition_root/models.py`: `39d8ea6da29ba54248c550917dcec6d5c0f2cf567e83c6b283aae6f20d4cafe8`
- `.roby/config.json`: `11a1dce801533fbe42bb37596e5273e2c9c99d52b2b26c625b7f54ee845132b5`
