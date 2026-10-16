# ROBY XI.2 — GATE 5.C.3.1 — SURGICAL GREEN

## Scope
Explicit Exact Investigation Scope → Analysis Mode TECHNICAL Read-Only Episode/Budget Projection.

## Productive change
Only `app/official_conversation_gateway.py` changes productively.

`OfficialConversationGateway.analysis_mode_projection(...)` now accepts the already-certified exact investigation scope as a query input, forwards that exact object to `UnifiedRuntimeObservability.snapshot(investigation_scope=...)`, and TECHNICAL projects the resulting canonical `snapshot.investigation_episode_budget`.

If no exact scope is supplied, the reasoning runtime is not provisioned, or no exact canonical retained episode exists, UnifiedRuntimeObservability yields `None` and TECHNICAL reports `investigation_episode_budget: not provisioned`.

## Preserved boundaries
- No owner/session/turn inference.
- No `last_session_id` substitution for exact scope.
- No latest/current/active episode selection.
- No private reasoning-store access from Analysis Mode.
- No direct call from Analysis Mode to `investigation_episode_budget_introspection(...)`.
- No global budget and no cross-domain episode fusion.
- No new manager, registry, graph, runtime, authority, persistence, or background loop.
- PERSONAL and ARCHITECTURAL selection semantics are not expanded.
- G5-R3d, G5-R3e, G5-R4, Memory/Learning and Planning N+1 remain STOP.
- `.roby/config.json`, `app/governed_reasoning_runtime.py`, and `app/unified_runtime_observability.py` are unchanged.

## Canonical chain
`InvestigationEpisodeBudgetObservabilityScope(owner, session_id, turn_id)`
→ `OfficialConversationGateway.analysis_mode_projection(...)`
→ `UnifiedRuntimeObservability.snapshot(investigation_scope=...)`
→ `OfficialGovernedReasoningRuntimeGateway.investigation_episode_budget_introspection(...)`
→ `UnifiedRuntimeObservabilitySnapshot.investigation_episode_budget`
→ Analysis Mode TECHNICAL read-only section.

## Validation performed in assistant environment
After regenerating M361, the focused gate/protection suite completed with **43 PASS · 0 FAIL**. `py_compile` for the changed productive module passed. Ruff is not installed in the assistant container, so Ruff certification is intentionally left to the user's local certification cycle.

Historical byte guards that legitimately protected the pre-5.C.3.1 conversation gateway were re-anchored to the new productive SHA; they were not removed.

## Post-delivery certification correction

User local validation of the first GREEN package exposed two packaging/contract defects before certification:

1. Ruff F821 on the forward annotation `InvestigationEpisodeBudgetObservabilityScope` in `app/official_conversation_gateway.py`.
2. Historical GATE 5.C.1 guard still prohibited any `investigation_episode_budget` mention in the conversation gateway, despite GATE 5.C.3.1 explicitly opening that read-only TECHNICAL projection.

The corrected GREEN does not broaden productive semantics. It adds a `TYPE_CHECKING`-only import for the already-certified `InvestigationEpisodeBudgetObservabilityScope`, avoiding a productive circular import, and re-anchors the historical guard to continue forbidding direct access to `_productive_explanatory_investigation_reentries` from the conversation gateway.

Corrected productive SHA-256:

- `app/official_conversation_gateway.py`: `7a2acbd485c997cbcf8373d0ee1d6e63d9f6a9a36aa97cd67c2661a3c0427ff2`

Corrected targeted validation:

- `python -m py_compile app/official_conversation_gateway.py`: PASS
- GATE 5.C.3.1 + 5.C.1 + 5.C.2.1 + 5.B.3.1 + M361: **44 PASS · 0 FAIL**
- Full local Ruff/full pytest certification remains user-side.
