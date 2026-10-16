# ROBY XI.2 — GATE 5.C.3.1 — CONTRACT RED

## Title
Explicit Exact Investigation Scope → Analysis Mode TECHNICAL Read-Only Episode/Budget Projection

## Certified entry baseline
GATE 5.C.3 — ARCHITECTURAL RECONCILIATION — CERTIFIED AND CLOSED.
User-local certification: 14,053 PASS · Ruff clean · 0 FAIL.

## Purpose
Freeze only the missing presentation boundary identified by GATE 5.C.3:

`explicit exact investigation scope`
→ `OfficialConversationGateway.analysis_mode_projection`
→ `UnifiedRuntimeObservability`
→ existing immutable `investigation_episode_budget` projection.

This gate creates no new authority and does not alter productive code in RED.

## Canonical scope
The gateway must reuse the already-certified frozen value object:

`InvestigationEpisodeBudgetObservabilityScope(owner, session_id, turn_id)`

No second Analysis Mode scope type, manager, registry, runtime, or authority is allowed.

## Frozen RED contracts
1. `analysis_mode_projection(...)` accepts one optional explicit `investigation_scope`.
2. The parameter reuses `InvestigationEpisodeBudgetObservabilityScope`; it does not reconstruct owner/session/turn.
3. TECHNICAL forwards that exact scope to `UnifiedRuntimeObservability.snapshot(...)`.
4. TECHNICAL selects only `snapshot.investigation_episode_budget`; it never calls the governed reasoning owner directly.
5. When no exact scope is supplied, or the canonical exact episode is absent, TECHNICAL reports `investigation_episode_budget: not provisioned` and does not synthesize state.
6. PERSONAL remains outside the episode/budget projection.
7. ARCHITECTURAL remains outside the episode/budget projection; G5-R4 stays STOP.
8. Analysis Mode keeps exactly PERSONAL / TECHNICAL / ARCHITECTURAL.
9. No inference from `last_session_id`, config, imports, wiring, names, tests, docs, filesystem, or any "latest/current/active episode" convention.
10. No private reasoning-store access and no call from Analysis Mode to `investigation_episode_budget_introspection(...)`.
11. No global budget and no fusion with epistemic/concept/abstraction/long-horizon stores.
12. No execution of Reasoning, Planning, Authorization, Execution, Reflection, Diagnostics, Memory, or Learning.
13. No new manager, registry, graph, runtime, authority, persistence, background work, or automation.
14. `app/unified_runtime_observability.py` remains byte-identical in RED.
15. `app/governed_reasoning_runtime.py` remains byte-identical in RED.
16. `.roby/config.json` remains byte-identical.
17. G5-R3d versions remains STOP.
18. G5-R3e certifications/quality remains STOP.
19. G5-R4 remains STOP.
20. Memory/Learning and Planning N+1 remain STOP.

## Productive files changed in CONTRACT RED
None.

## Expected RED
Only the missing Analysis Mode seam should fail: explicit scope parameter, exact forwarding, TECHNICAL selection, and honest not-provisioned presentation.
All existing certified architecture must remain green.

## GREEN boundary if RED is certified
A future SURGICAL GREEN may modify only the smallest existing Analysis Mode projection boundary necessary to satisfy this contract. It must not modify UnifiedRuntimeObservability or the governed reasoning owner unless a new reconciliation explicitly proves that necessary.
