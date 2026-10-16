# ROBY XI.2 — MASTER PLAN

## Unified Experience Provider-Response Reachability — SURGICAL GREEN

### Classification

- Block: SURGICAL GREEN
- Starting state: CONTRACT RED / OWNER-CERTIFIED
- Starting RED: 5 expected failures / 13,333 other tests passed
- Starting Ruff after corrected imports: clean
- New capability: NONE
- New authority: NONE
- B2 / B3 / B4: STOP

### Closed residual

`UNIFIED_EXPERIENCE_PROVIDER_RESPONSE_REACHABILITY`

The ordinary provider path now reuses the existing canonical
`UnifiedExperienceLayer`.

No second experience or humanization authority was created.

### Surgical implementation

The GREEN adds one typed method to the existing layer:

`present_operational_response()`

It accepts an immutable `OperationalResponse` and returns an
`OperationalResponse`.

The method reuses the existing presentation policy. It does not create another
presentation algorithm or policy owner.

If visible text is unchanged, the original operational response is returned.

If visible text changes, `dataclasses.replace()` creates a new immutable response
with only:

- `response_text` changed;
- `response_id` cleared for canonical recomputation.

All other operational fields remain inherited from the assembled response.

### Canonical pipeline seam

The existing `GovernedOperationalConversationPipeline` now accepts one optional
`experience_layer` dependency.

On the ordinary provider path the order is:

1. provider execution;
2. optional retrieval;
3. response assembly;
4. canonical Unified Experience presentation;
5. status derivation;
6. final governed pipeline result;
7. repository persistence.

This closes the exact PRE-RED seam:

`POST_ASSEMBLY_PRE_RESULT`

The interceptor path remains separate and unchanged.

### Composition reuse

`RuntimeCompositionDependencies` now transports the already-existing canonical
experience-layer instance.

`RuntimeCompositionRoot` passes that dependency into the existing conversation
pipeline.

`runtime_root_factory` still creates exactly one `UnifiedExperienceLayer`, registers
it on the official capability registry, and passes that same instance through the
existing composition boundary.

No second layer is constructed.

### Preserved operational lineage

The presentation operation preserves:

- request;
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

No evidence, provider truth, retrieval truth, authorization, action, or operational
status is created or reinterpreted by presentation.

### Identity semantics

When visible text changes, the existing `OperationalResponse` model recomputes its
identity from the final content and preserved lineage.

The subsequent `GovernedConversationPipelineResult` then derives its existing
deterministic identity from the final operational response.

No stale `response_id` or `result_id` is copied.

### Compatibility and failure boundaries

The experience dependency is optional.

When absent, historical provider behavior remains unchanged.

This GREEN adds no second provider call, retrieval, hidden retry, platform mutation,
or alternate response assembler.

### Protected horizons

This block does not integrate or reopen:

- Relationship Memory;
- Presence;
- Social Regulation;
- simulated inner state;
- inner continuity;
- conversation reflection;
- new M377 signals;
- personality learning;
- Desktop presentation ownership;
- Voice Identity;
- legacy `CognitivePipeline`.

M55 -> M377 remains closed and certified.

### Verification

The corrected Owner-provided RED test with canonical import ordering is integrated.

Directed contract:

`7 passed`

Focused Unified Experience / M177 conversational regression set:

`127 passed`

All modified productive Python files compile.

No new line longer than 88 characters was introduced in modified files.

The complete owner-side global chain remains required before global certification.

### Closure

`PROVIDER_RESPONSE_UNIFIED_EXPERIENCE: PRODUCTIVELY_REACHABLE`

`CANONICAL_PROVIDER_PRESENTATION_POINT: POST_ASSEMBLY_PRE_RESULT`

`UNIFIED_EXPERIENCE_AUTHORITY: SINGLE / REUSED`

`OPERATIONAL_LINEAGE: PRESERVED`

`SURGICAL_GREEN: LOCAL_GREEN`

`NEXT_ACTION: OWNER_GLOBAL_CERTIFICATION`

B2 / B3 / B4 remain in STOP.
