# ROBY XI.2 — MASTER PLAN

## Unified Experience Provider-Response Reachability — CONTRACT RED

### Classification

- Block: CONTRACT RED
- Starting state: PRE-RED RECONCILIATION CLOSED
- Product change: NONE
- Authority change: NONE
- New capability: NONE
- Expected state after this block: RED
- B2 / B3 / B4: STOP

### Contractual residual

The authorized residual is:

`UNIFIED_EXPERIENCE_PROVIDER_RESPONSE_REACHABILITY`

The canonical `UnifiedExperienceLayer` already exists and already serves intercepted
responses. Ordinary provider responses still bypass it.

This contract does not authorize another experience authority.

### Required future seam

The future GREEN must reuse the same canonical `UnifiedExperienceLayer`.

The provider-response seam is:

`response assembly -> presentation -> final pipeline result`

The presentation operation must be typed:

`OperationalResponse -> OperationalResponse`

It must not coerce an ordinary provider response into
`GovernedOperationalInterception`.

### Required preservation

Only visible `response_text` may change.

The future projection must preserve:

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

When visible text changes, the existing immutable model must recompute the response
identity. The final pipeline result must then derive its normal identity from that
final response.

Stale response or result identities must not be copied.

### Existing composition boundary

The existing `RuntimeCompositionDependencies` boundary may transport the already
created canonical experience layer to the existing conversation pipeline.

The factory must continue to construct exactly one `UnifiedExperienceLayer`.

The existing operational interceptor remains interception authority only and must not
be repurposed as presentation authority.

### Compatibility

Absence of the optional presentation dependency must preserve historical provider
behavior.

No second provider call, retrieval, hidden retry, platform mutation, or alternate
presentation authority is authorized.

### Protected boundaries

This RED does not authorize:

- a second experience layer;
- a response humanizer or presentation manager;
- Relationship Memory integration;
- Presence integration;
- Social Regulation integration;
- simulated inner-state projection;
- reflection projection;
- new adaptive-personality signals;
- personality learning;
- Desktop presentation ownership;
- Voice Identity;
- provider-owned humanization;
- legacy `CognitivePipeline` activation;
- a second response assembler;
- a second ordinary conversation pipeline.

M55 -> M377 remains closed.

### Expected RED

The contract is expected to fail because current executable state lacks:

1. a typed provider-response presentation operation on the existing layer;
2. one optional experience dependency on the existing pipeline;
3. post-assembly / pre-result provider presentation;
4. transport of the same canonical layer through existing composition.

Guardrails against interceptor repurposing and parallel humanization authorities may
already pass.

No GREEN implementation belongs to this block.

### Closure criterion

A valid RED has only the expected missing-seam failures.

Unexpected architecture failures require reconciliation before GREEN.

`NEXT_ACTION_AFTER_OWNER_RED_CERTIFICATION:
UNIFIED_EXPERIENCE_PROVIDER_RESPONSE_REACHABILITY_SURGICAL_GREEN`

B2 / B3 / B4 remain in STOP.
