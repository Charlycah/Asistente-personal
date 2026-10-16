# ROBY XI.2 — GATE 5.C.3
## Existing UnifiedRuntimeObservability Exact Episode/Budget Projection → Analysis Mode TECHNICAL — ARCHITECTURAL RECONCILIATION

## 1. Purpose

Reconcile the already-certified GATE 5.C.2.1 exact-scope investigation episode/budget projection with the existing Analysis Mode TECHNICAL boundary before any productive change is authorized.

This gate is reconciliation only. It does not add productive behavior to Analysis Mode, does not create a new authority, and does not relax the exact-scope governance established in GATE 5.C.1 / 5.C.2.1.

## 2. Baseline certification hygiene correction

The local GREEN validation for GATE 5.C.2.1 reached 14,053 PASS before Ruff corrected one import-order I001 in `app/unified_runtime_observability.py`. That import-only correction changed the file SHA after the full pytest run.

The post-Ruff productive SHA is:

- `app/unified_runtime_observability.py`
  - `63ddb40534e275d0879504b35c31426735d16aaa0064b5dc53ffcde2fd719681`

Two historical byte guards still referenced the pre-Ruff SHA `970b141c...`. This reconciliation package re-anchors only those guards to the post-Ruff SHA. No productive semantics are changed by that guard re-anchor.

Re-anchored test-only files:

- `tests/architecture/test_gate5c21_explicit_exact_investigation_scope_unified_observability_episode_budget_projection_contract_red.py`
- `tests/architecture/test_gate5b41_unified_observability_capability_dependencies_analysis_mode_technical_contract_red.py`

Targeted validation after re-anchor:

- 33 PASS
- 0 FAIL

A full local M361 + Ruff + pytest cycle remains required before this reconciliation is formally certified.

## 3. Existing certified canonical chain

GATE 5.C.2.1 already provides:

`InvestigationEpisodeBudgetObservabilityScope(owner, session_id, turn_id)`
→ `UnifiedRuntimeObservability.snapshot(..., investigation_scope=...)`
→ `runtime.root.dependencies.governed_reasoning_runtime`
→ `OfficialGovernedReasoningRuntimeGateway.investigation_episode_budget_introspection(...)`
→ `UnifiedRuntimeObservabilitySnapshot.investigation_episode_budget`

The scope object is frozen and contains exactly:

- `owner`
- `session_id`
- `turn_id`

The snapshot projection is fail-closed:

- no explicit scope → `None`
- no governed reasoning runtime → `None`
- no exact retained canonical episode → `None`
- exact retained canonical episode → exact frozen owner-level view

No private reasoning store is scanned and no global/latest episode is synthesized.

## 4. Existing Analysis Mode TECHNICAL boundary

`OfficialConversationGateway.analysis_mode_projection(runtime, *, session_id=None)` currently:

1. resolves Analysis Mode status from the session;
2. calls `UnifiedRuntimeObservability().snapshot(runtime)` with no investigation scope;
3. selects a bounded read-only TECHNICAL subset:
   - operational
   - readiness
   - conversation
   - registered_capabilities
   - capability_registry
   - cognitive_core
   - self_diagnostics
   - capabilities when available
   - capability_dependencies when provisioned
   - recovery when provisioned

It does not select `snapshot.investigation_episode_budget`.

## 5. Exact-scope gap

The current Analysis Mode projection API has only:

- `runtime`
- optional `session_id`

It does not receive:

- exact `owner`
- exact `turn_id`
- an `InvestigationEpisodeBudgetObservabilityScope`

`OfficialConversationGatewaySnapshot` contains `last_session_id` but does not contain owner or turn_id.

The gateway does use an owner from runtime bootstrap configuration in other conversational paths, and `LocalConversationTurn` contains owner/session_id/turn_id, but neither fact authorizes Analysis Mode to reconstruct or infer the exact investigation scope.

The exact triple required by GATE 5.C.2.1 must not be assembled from unrelated local facts, latest-turn assumptions, bootstrap configuration, sequence numbers, pipeline IDs, or private stores.

## 6. Architectural classification

**CANONICAL EXACT-SCOPE OWNER VIEW EXISTS + UNIFIED RUNTIME OBSERVABILITY EXACT PROJECTION EXISTS + ANALYSIS MODE TECHNICAL READ-ONLY SELECTION EXISTS + ANALYSIS MODE HAS NO EXPLICIT EXACT INVESTIGATION-SCOPE INPUT.**

The residual is therefore not a missing authority and not missing runtime reachability.

The residual is one explicit query-boundary step:

`caller-supplied exact investigation scope`
→ `OfficialConversationGateway Analysis Mode TECHNICAL`
→ `UnifiedRuntimeObservability.snapshot(..., investigation_scope=scope)`
→ existing immutable episode/budget projection

## 7. Forbidden solutions

The following remain forbidden:

- infer owner from bootstrap configuration for this projection;
- infer session from `last_session_id` as sufficient scope;
- infer turn_id from latest conversation turn, sequence, pipeline result, observation ID, or any naming convention;
- inspect or scan `_productive_explanatory_investigation_reentries` or any private reasoning store;
- select a "latest", "current", or "active" episode without an exact supplied scope;
- create an EpisodeRegistry, BudgetManager, AnalysisScopeManager, new runtime, new graph, or parallel authority;
- synthesize a global budget;
- fuse investigation state with epistemic, abstraction, concept, or long-horizon stores;
- execute Reasoning, Planning, Authorization, Execution, Reflection, Memory, or Learning to obtain the projection;
- change PERSONAL Analysis Mode semantics;
- change ARCHITECTURAL Analysis Mode or open G5-R4;
- open G5-R3d versions;
- open G5-R3e certifications/quality;
- modify `.roby/config.json`.

## 8. Recommended next gate

Only after this reconciliation is locally certified and explicitly authorized:

**GATE 5.C.3.1 — Explicit Exact Investigation Scope → Analysis Mode TECHNICAL Read-Only Episode/Budget Projection — CONTRACT RED**

Recommended RED boundary:

1. Analysis Mode projection accepts one explicit exact investigation scope as query input; no inference.
2. The scope is forwarded unchanged to `UnifiedRuntimeObservability.snapshot(...)`.
3. PERSONAL remains unchanged and must not request/publish investigation episode/budget.
4. ARCHITECTURAL remains unchanged and must not request/publish investigation episode/budget.
5. TECHNICAL with no explicit scope must not select any episode or call the canonical owner for one.
6. TECHNICAL with an explicit scope and a present canonical view publishes one read-only `investigation_episode_budget` section.
7. TECHNICAL with explicit scope but no canonical retained episode reports honest unavailability rather than a synthetic view.
8. No direct access from Analysis Mode to `governed_reasoning_runtime` or its private stores.
9. No new manager/registry/runtime/authority/persistence.
10. Existing capability dependency projection remains unchanged.
11. Existing Analysis Mode session scoping remains unchanged.
12. `.roby/config.json` remains byte-identical.

The smallest design is to reuse the existing frozen `InvestigationEpisodeBudgetObservabilityScope` as caller-supplied query data, imported lazily if needed to preserve module boundaries. No second scope type is justified.

## 9. Protected productive hashes at reconciliation

- `app/unified_runtime_observability.py`
  - `63ddb40534e275d0879504b35c31426735d16aaa0064b5dc53ffcde2fd719681`
- `app/official_conversation_gateway.py`
  - `737ba00cb82cf58dd890876996af52d74b9efad57e11641ebb5918671567b9c9`
- `app/governed_reasoning_runtime.py`
  - `26a9f4f6c1fb629f857f5b2943b9d80a56edc641ba38a730e900317704e008ba`
- `core/runtime_composition_root/models.py`
  - `39d8ea6da29ba54248c550917dcec6d5c0f2cf567e83c6b283aae6f20d4cafe8`
- `.roby/config.json`
  - `11a1dce801533fbe42bb37596e5273e2c9c99d52b2b26c625b7f54ee845132b5`

## 10. Reconciliation result

No productive Analysis Mode change is justified inside GATE 5.C.3 itself.

The architecture already has the canonical owner, exact immutable owner-level view, runtime reachability, and unified projection. The only remaining seam before TECHNICAL publication is explicit propagation of the exact already-governed query scope through the Analysis Mode boundary.

**GATE 5.C.3 classification: READY FOR CONTRACT RED AFTER LOCAL RECONCILIATION CERTIFICATION.**
