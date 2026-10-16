# ROBY XI.2 — MASTER PLAN

## Unified Experience Provider-Response Reachability — PRE-RED Reconciliation

## 1. Classification

- Block: PRE-RED RECONCILIATION / DOCUMENTARY ONLY
- Product change: NONE
- Test change: NONE
- New capability: NONE
- Authority change: NONE
- Starting baseline: OWNER-CERTIFIED / GLOBAL GREEN
- Starting suite: 13,331 passed / 0 failed
- Starting Ruff: clean
- B2 / B3 / B4: STOP

This block follows the certified M55 -> M377 ordinary-turn personality projection.
It does not reopen that seam.

## 2. Governing question

The preceding horizon reconciliation selected one residual:

`UNIFIED_EXPERIENCE_PROVIDER_RESPONSE_REACHABILITY`

The question is not whether ROBY needs another presentation or humanization layer.
It already has one canonical `UnifiedExperienceLayer`.

The question is narrower:

Can the existing layer productively refine the visible text of an ordinary provider
response without changing operational truth, execution authority, evidence, provider
lineage, retrieval lineage, network lineage, or result identity semantics?

No RED is authorized until the exact type and composition seam is demonstrated.

## 3. Existing authority

`app/unified_experience_layer.py` owns `UnifiedExperienceLayer`.

The factory creates exactly one instance and installs it on the existing official
capability registry with `set_experience_layer()`.

The registry already invokes `experience_layer.present()` for governed intercepted
results.

Therefore:

`UNIFIED_EXPERIENCE_AUTHORITY: EXISTING / CANONICAL`

A second experience layer, response humanizer, personality renderer, presentation
manager, agent, runtime, loop, or provider-side formatter is not authorized.

## 4. Existing intercepted-response reachability

`RuntimeCapabilityRegistry._present()` delegates to the installed experience layer.

This proves productive reachability for intercepted operational results.

It does not prove provider-response reachability.

Therefore:

`INTERCEPTED_RESPONSE_UNIFIED_EXPERIENCE: REACHABLE`

`PROVIDER_RESPONSE_UNIFIED_EXPERIENCE: MISSING`

The missing behavior is integration, not a new capability.

## 5. Ordinary provider path

The current ordinary provider path is:

1. `GovernedOperationalConversationPipeline.process()`;
2. canonical preparation;
3. provider execution;
4. optional retrieval execution;
5. `response_assembler.assemble(...)`;
6. `OperationalResponse`;
7. status derivation;
8. `GovernedConversationPipelineResult`;
9. repository storage;
10. return to the existing conversation path.

After step 5, no existing call to the canonical `UnifiedExperienceLayer` is shown for
the provider response.

This is the demonstrated causal gap.

## 6. Type boundary

`UnifiedExperienceLayer.present()` currently accepts and returns
`GovernedOperationalInterception | None`.

An ordinary provider result is not a `GovernedOperationalInterception`.

Its visible text lives in `OperationalResponse.response_text`.

`OperationalResponse` additionally owns operational lineage including:

- status;
- action;
- evidence;
- limitations;
- provider execution id;
- retrieval execution id;
- provider-call flag;
- retrieval flag;
- network-access flag;
- platform-mutation flag;
- rationale;
- timestamp;
- deterministic response identity.

Converting an `OperationalResponse` into a fake interception would collapse or
misrepresent this lineage.

Therefore:

`INTERCEPTION_COERCION: FORBIDDEN`

## 7. Result lineage constraint

`GovernedConversationPipelineResult` validates exact consistency between itself and
its `OperationalResponse`.

It also includes `operational_response.response_id` in its own deterministic identity.

Consequently, post-hoc replacement of visible text after the final pipeline result
has been created is not an admissible seam.

If presentation legitimately changes `response_text`, the response identity must be
derived from the presented response, and the pipeline result identity must then be
derived from that response.

Therefore:

`POST_RESULT_TEXT_MUTATION: FORBIDDEN`

`PRESENTATION_BEFORE_FINAL_RESULT_ASSEMBLY: REQUIRED`

## 8. Smallest canonical seam

The smallest demonstrated seam is inside the existing
`GovernedOperationalConversationPipeline.process()` after:

`response_assembler.assemble(...)`

and before:

- status derivation;
- `GovernedConversationPipelineResult(...)`;
- repository persistence.

This location already has:

- the original conversation request;
- the complete assembled `OperationalResponse`;
- all operational lineage;
- no need for a second provider call;
- no need for a second response assembler;
- no need for a second conversation pipeline.

Decision:

`CANONICAL_PROVIDER_PRESENTATION_POINT: POST_ASSEMBLY_PRE_RESULT`

## 9. Required authority transport

The pipeline currently receives `operational_interceptor`, but that port represents
interception authority and must not be repurposed as presentation authority.

The existing composition root already owns the dependency boundary used to construct
the single conversation pipeline.

A future GREEN may transport the already-created canonical
`UnifiedExperienceLayer` through that existing composition boundary into the existing
pipeline.

This is dependency wiring, not a new authority.

Decision:

`UNIFIED_EXPERIENCE_DEPENDENCY: EXISTING_CANONICAL_INSTANCE_ONLY`

`OPERATIONAL_INTERCEPTOR_REPURPOSING: FORBIDDEN`

## 10. Required typed operation

The current `present()` contract is interception-specific.

The future contract may require the same `UnifiedExperienceLayer` to expose one
bounded typed operation for an `OperationalResponse`.

That operation must reuse the layer's existing presentation/refinement policy rather
than duplicate it.

It may alter only the visible `response_text`.

Every other operational field must be preserved from the assembled response.

The returned object must remain an `OperationalResponse`.

Decision:

`PROVIDER_PRESENTATION_TYPE: OPERATIONAL_RESPONSE_TO_OPERATIONAL_RESPONSE`

## 11. Identity semantics

`OperationalResponse` is immutable and deterministically identified.

If its visible text changes through the authorized presentation layer, constructing
a new immutable `OperationalResponse` is legitimate.

The new response identity must be the canonical identity derived by the existing
model from the final visible response and preserved lineage.

No caller may copy the old `response_id` onto changed content.

The subsequent `GovernedConversationPipelineResult` must likewise derive its normal
identity from the final response.

Decision:

`IDENTITY_RECOMPUTATION: USE_EXISTING_MODEL_SEMANTICS`

`STALE_RESPONSE_ID_COPY: FORBIDDEN`

`STALE_RESULT_ID_COPY: FORBIDDEN`

## 12. Lineage preservation contract

A future RED must require exact preservation of all non-presentation fields:

- request object;
- status;
- action;
- evidence;
- limitations;
- provider execution id;
- retrieval execution id;
- provider-call flag;
- retrieval flag;
- network-access flag;
- platform-mutation flag;
- rationale;
- created-at timestamp.

Presentation must not create, remove, reinterpret, or authorize evidence.

Presentation must not change provider or retrieval truth.

Presentation must not convert failure into success or success into failure.

Presentation must not change operational action.

## 13. Scope of visible refinement

The existing Unified Experience authority may continue to own its already-governed
visible-response refinements.

This PRE-RED does not authorize new conversational psychology or new style policy.

It authorizes only reuse of the existing authority on the previously unreachable
ordinary provider-response path.

Therefore:

`NEW_EXPERIENCE_POLICY: NONE`

`NEW_HUMANIZATION_AUTHORITY: NONE`

## 14. Failure and compatibility behavior

The ordinary provider path must remain fail-closed.

Absence of a Unified Experience dependency must preserve historical behavior.

A presentation failure must not trigger a second provider call, second retrieval,
platform mutation, hidden retry, or alternate authority.

The RED must explicitly protect the existing no-presentation compatibility path.

## 15. Boundaries retained from the humanization map

This residual does not authorize:

- Relationship Memory integration;
- Presence integration;
- Social Regulation integration;
- simulated inner-state projection;
- inner continuity projection;
- conversation-reflection projection;
- new M377 signals;
- personality learning;
- Voice Identity;
- Desktop presentation ownership;
- provider-owned humanization;
- reactivation of the historical rich `CognitivePipeline`;
- a second experience layer;
- a second operational response assembler;
- a second ordinary conversation pipeline.

M55 -> M377 remains closed and certified.

## 16. CONTRACT RED shape

Evidence is sufficient for a narrow CONTRACT RED.

The contract should prove that:

1. the existing pipeline has one optional canonical Unified Experience dependency;
2. provider responses are presented only post-assembly and pre-final-result;
3. the same canonical layer instance from the factory is reused;
4. the typed operation returns `OperationalResponse`;
5. only `response_text` may differ;
6. all operational lineage is preserved exactly;
7. deterministic identities are recomputed through existing model semantics;
8. interception authority is not repurposed;
9. missing presentation dependency preserves historical behavior;
10. no parallel humanization authority or forbidden cognitive integration appears.

The RED must fail because current executable state lacks this provider-response
presentation seam, not because of unrelated historical assumptions.

## 17. PRE-RED closure

`UNIFIED_EXPERIENCE_AUTHORITY: EXISTING / CANONICAL`

`INTERCEPTED_RESPONSE_UNIFIED_EXPERIENCE: REACHABLE`

`PROVIDER_RESPONSE_UNIFIED_EXPERIENCE: MISSING`

`INTERCEPTION_COERCION: FORBIDDEN`

`CANONICAL_PROVIDER_PRESENTATION_POINT: POST_ASSEMBLY_PRE_RESULT`

`PROVIDER_PRESENTATION_TYPE: OPERATIONAL_RESPONSE_TO_OPERATIONAL_RESPONSE`

`LINEAGE_PRESERVATION: REQUIRED`

`IDENTITY_RECOMPUTATION: EXISTING_MODEL_SEMANTICS`

`RED_AUTHORIZED: YES`

`NEXT_ACTION: UNIFIED_EXPERIENCE_PROVIDER_RESPONSE_REACHABILITY_CONTRACT_RED`

B2 / B3 / B4 remain in STOP.
