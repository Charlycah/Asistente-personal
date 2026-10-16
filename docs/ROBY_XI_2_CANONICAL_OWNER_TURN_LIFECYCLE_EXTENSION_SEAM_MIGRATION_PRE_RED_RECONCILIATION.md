# ROBY XI.2 — Canonical Owner-Turn Lifecycle Extension Seam
## Migration PRE-RED Reconciliation

## Owner-certified starting state

The architectural decision is Owner-certified at:

- 13,479 tests passed;
- 0 tests failed;
- Ruff clean.

It authorizes in principle a Class-2 deepening of the existing canonical
`OfficialConversationGateway`.

It does not authorize productive modification yet.

This PRE-RED changes no productive Python code and adds no RED tests.

## 1. Historical gateway-hash migration matrix

Repository-wide exact search found 28 architecture-test files containing the
certified predecessor gateway SHA:

`0f8896575116a7ebaac908486d897e22c2f6adff59a05b3cc2997d028b5e0b11`

The complete file matrix is:

- `test_authorized_goal_productive_investigation_routing.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_post_12760_governed_pipeline_explicit_multisource_selection_representation_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_post_12776_single_reasoning_multisource_convergence_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_gate5c21_explicit_exact_investigation_scope_unified_observability_episode_budget_projection_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_post_12736_shared_evidence_visual_relational_compatibility_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_official_runtime_exact_authorized_memory_write_reentry.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_post_12782_product_surface_explicit_multisource_selection_gateway_reachability_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_official_desktop_same_turn_visual_composition_root_binding_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_g6_approved_learning_g7_materialization_productive_reachability.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_post_12755_canonical_explicit_evidence_composition_dependency_placement_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_post_12766_local_conversation_runtime_explicit_multisource_selection_transport_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_e1_b_s1_c_certified_proposal_review_transport_desktop_composition_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_m369_evaluation_g6_explicit_human_approval_productive_reachability.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_r_evo_s1_o_evidence_lineage_reentry_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_gate5c31_explicit_exact_investigation_scope_analysis_mode_technical_episode_budget_projection_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_p7_c2_local_s2b_a_authorized_execution_m400_ingress_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_m369_learning_candidate_evaluation_productive_reachability.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_post_12748_ordinary_turn_productive_reachability_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_r_evo_s1_i_productive_consumer_reachability_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_p7_c2_local_s2a_provider_source_credential_gated_enablement_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_r_mp_h4_voice_s2_canonical_adaptive_delivery_tone_productive_spoken_response_reachability_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_gate5b31_canonical_runtime_capability_graph_unified_observability_dependency_snapshot_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_p7_c2_local_s2c_a_official_runtime_foursquare_provider_availability_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_cap11_terminal_closure_m369_candidate_productive_reachability.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_post_12741_same_episode_explicit_evidence_convergence_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_post_12787_documentary_current_truth_root_authority_precedence_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_r_evo_s1_f3_external_productive_continuity_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.
- `test_post_12729_personal_document_governed_reasoning_explicit_evidence_admission_contract_red.py` — migrate gateway whole-file hash only; retain every other guard.

These assertions come from independently certified increments whose local
architectural rule was "do not solve this block by gateway surgery."

That historical rule remains true for those increments.

The newly Owner-certified architectural decision is a later, explicit Class-2
migration of the gateway itself.

Therefore all 28 files require the same narrow migration classification:

`MIGRATE GATEWAY WHOLE-FILE HASH GUARD ONLY`

This does not authorize removal of their other hashes, source assertions,
authority checks, no-duplication checks, reachability checks, or behavior
contracts.

No test may receive a replacement gateway SHA as the migration.

## 2. Replacement compatibility strategy

The old hash remains documentary predecessor evidence.

For the 28 affected tests, compatibility must be protected by two layers.

### Layer A — original local semantic guards

Every non-gateway-hash assertion in each historical test remains unchanged.

This preserves the capability each original increment was certifying.

### Layer B — canonical gateway regression suite

The migration must rely on existing gateway behavior tests plus new applied
lifecycle contracts.

Existing semantic anchors already prove:

- gateway is the only turn-submission boundary;
- desktop text and voice share that gateway;
- ordinary runtime failure behavior;
- interceptor precedence;
- submitted-turn accounting;
- cycle sealing;
- post-turn observer execution;
- runtime bypass for recognized internal interceptors;
- UnifiedBrain observability derives from gateway state.

Representative existing tests include:

- `test_rp_18_4_single_conversation_route.py`;
- `test_m386_18_official_entry_identification_integration.py`;
- `test_post_m409_1_explicit_deliberation_productive_advisory_wiring.py`;
- `test_m386_11_conversation_entry_evidence_adapter.py`;
- `test_m386_12_unified_coordination_evidence_adapter.py`;
- `test_m387_8_post_turn_reflection_learning.py`;
- `test_m382_6_unified_brain_observability.py`.

The future RED must add applied-specific compatibility without weakening these.

## 3. Exact gateway insertion point

The correct insertion point is demonstrated inside
`OfficialConversationGateway.submit`.

It is inside the existing nested evidence/identity capture scopes and inside
the existing `try`, but before the ordinary `converse_runtime(...)` fallback.

The applied branch must be subordinate to existing higher-priority internal
interceptors and explicit current-turn context.

The exact shape is:

`EXISTING INTERCEPTORS`
`-> APPLIED ELIGIBILITY BRANCH`
`-> EXISTING converse_runtime FALLBACK`
`-> EXISTING RELATIONAL/RESPONSE/REFLECTION FINALIZATION`
`-> EXISTING ACCOUNTING/OBSERVER/EVIDENCE EPILOGUE`

This preserves failure closure because applied execution remains inside the
existing gateway `try`.

## 4. Applied eligibility and precedence

The applied branch is eligible only when all explicit current-turn selection
inputs are absent:

- `explicit_document_ids`;
- `explicit_sources`;
- `explicit_evidence_references`;
- `integrated_visual_context`.

Existing higher-priority gateway interceptors retain precedence.

`external_evidence` must retain the same safe fallback semantics already used
by existing internal interceptors unless the future RED proves otherwise.

This PRE-RED does not authorize broadening applied reachability.

## 5. Applied-result exposure inventory

No existing gateway per-turn field, property, evidence adapter, runtime result,
or snapshot stores the exact
`AppliedConversationalIntelligenceResult` object identity.

Existing cognitive/evidence snapshots are redacted semantic/technical
observability surfaces, not arbitrary result-object carriers.

Therefore exact same-turn applied-result identity cannot currently be recovered
after `submit` without either:

- recomputing applied execution, which is forbidden; or
- adding one bounded result exposure during the authorized gateway migration.

This is a demonstrated residual.

## 6. Exposure decision for CONTRACT RED

The future RED may contract a bounded gateway-owned exposure of the exact
applied result produced by the most recently completed recognized applied turn.

The exposure must:

- be read-only to callers;
- be cleared before every owner-turn attempt;
- remain `None` for normal/interceptor/explicit-context turns;
- be assigned only from the exact successful applied execution;
- be cleared on failure;
- never execute or reinterpret text when read;
- never become persistence, Memory, Knowledge, or a new authority;
- preserve object identity;
- be scoped to same-process completed-turn consumption.

The exact public name is intentionally left for CONTRACT RED naming, but its
semantics are now sufficiently bounded.

## 7. Applied turn construction

The canonical gateway already contains the correct interceptor construction
precedent.

Its internal turn builders use:

- configured owner;
- effective session id;
- `self._submitted_turns + 1`;
- `response_path="interceptor"`;
- timezone-aware creation time;
- existing common lifecycle finalization.

The future applied branch should follow this pattern.

It must not rely on external reads of `_runtime` or `_submitted_turns`.

## 8. Additive composition migration

The certified
`applied_conversational_intelligence_owner_turn_composition.py`
currently duplicates two semantics that will become gateway-owned:

- applied eligibility/fallback branching;
- applied `LocalConversationTurn` construction.

After canonical migration, keeping those semantics independently executable
would create duplicate branch ownership.

Therefore the future GREEN must not leave both implementations authoritative.

Migration direction:

`CANONICAL GATEWAY OWNS EXECUTION AND TURN CONSTRUCTION`

The additive composition may remain only as a compatibility/delegation surface
that calls the canonical gateway once and reads the bounded exact result
exposure.

It must no longer call
`execute_applied_conversational_intelligence` independently.

Its existing public result type may be preserved to avoid downstream schema
churn.

## 9. Failure-path proof

The selected insertion point is inside the existing gateway `try`.

Therefore any exception from applied interpretation, source selection, source
execution, natural response composition, or applied-turn construction reaches
the existing:

- cognitive observer failure;
- conversation-entry evidence seal;
- re-raise path.

The future RED must assert:

- no submitted-turn increment on failure;
- no retained applied result on failure;
- no active evidence cycle remains;
- no fallback second execution after applied failure.

## 10. UnifiedBrain preservation

No change to `app/unified_brain.py` is required by the selected architecture.

Current SHA remains:

`05f4c65fbb8a1478f9117b9b1de8c450d15211a257aa4835b8123a6babbc1750`

The future migration must prove it remains byte-identical.

Its existing `submit_observed` callback continues to provide reflection exactly
once, and completed-turn cognitive analysis remains after gateway completion.

## 11. CONTRACT RED readiness

All required migration questions are now answered:

- 28 old gateway-hash test files inventoried;
- migration rule defined without mechanical replacement hash;
- semantic compatibility strategy identified;
- exact lifecycle insertion region identified;
- precedence bounded;
- exact applied-result exposure gap demonstrated;
- gateway-owned bounded exposure semantics defined;
- additive composition migration direction defined;
- failure closure demonstrated structurally;
- UnifiedBrain preservation demonstrated.

Therefore:

`CONTRACT RED: AUTHORIZABLE AFTER OWNER CERTIFICATION OF THIS PRE-RED`

The RED must remain test/documentation-only.

It may deliberately fail on:

- absent canonical applied branch inside `submit`;
- absent bounded exact-result exposure;
- additive composition still independently executing applied intelligence;
- historical hash guards not yet migrated as contracted.

The RED must not modify productive code.

## 12. Separate residuals

Still outside scope:

`OFFICIAL_DESKTOP_VISUAL_COMPOSITION_ROOT_PRODUCTIVE_BINDING`

`EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY`

`EXTERNAL_IMAGE_FRESHNESS_ORDERING`

No `mostrame fotos` recognition or `ultimas` ordering belongs here.

## Status

`CANONICAL_OWNER_TURN_LIFECYCLE_EXTENSION_SEAM_MIGRATION_PRE_RED:
COMPLETE / PENDING OWNER CERTIFICATION`

`OLD GATEWAY HASH ASSERTION FILES: 28`

`MIGRATION: SEMANTIC / NO MECHANICAL REPLACEMENT HASH`

`EXACT INSERTION REGION: DEMONSTRATED`

`EXACT APPLIED-RESULT EXPOSURE GAP: DEMONSTRATED`

`CANONICAL EXECUTION OWNER: OfficialConversationGateway`

`ADDITIVE COMPOSITION: FUTURE COMPATIBILITY/DELEGATION SURFACE`

`UNIFIED BRAIN: BYTE-PRESERVE`

`CONTRACT RED: AUTHORIZABLE ONLY AFTER OWNER CERTIFICATION`

`NEW AUTHORITY: NONE`

STOP for Owner local certification.
