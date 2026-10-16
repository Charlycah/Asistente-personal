# ROBY XI.2 — INTEL-G10 — SURGICAL GREEN

## Gate

**SOURCE-NEUTRAL CERTIFIED GOVERNED MEMORY WRITE REQUEST → OFFICIAL CONVERSATION GATEWAY → EXISTING PRODUCTIVE GOVERNED LEARNING WIRING**

Status: **SURGICAL GREEN — pending final local certification**.

Input baseline: **INTEL-G9 SURGICAL GREEN locally certified — 14,117 PASS · Ruff clean · 0 FAIL · 0 regressions**.

## Implemented residual

G10 adds only the explicit productive invocation seam reconciled and frozen by CONTRACT RED:

`GovernedMemoryWriteRequest` already certified
→ existing `OfficialConversationGateway.submit(...)`
→ existing `ProductiveGovernedLearningWiring.execute_certified_write_request(...)`
→ existing `OfficialMemoryGateway`
→ existing governed Memory runtime.

`OfficialConversationGateway.submit(...)` now exposes the keyword-only input:

`governed_memory_write_request=None`

When present and no external evidence is being admitted, the exact request object is forwarded to the already-certified G9 seam. The gateway does not evaluate, authorize, materialize, adapt, reconstruct, or mutate the request.

## Authority preservation

The implementation does not create or replace any authority.

- `OfficialConversationGateway` remains the sole governed interactive entry boundary.
- `ProductiveGovernedLearningWiring` remains the existing productive governed-learning wiring authority.
- `GovernedMemoryWriteAdapterFoundation` remains the existing certified proposal-to-request adapter.
- `OfficialMemoryGateway` remains the sole governed Memory write authority.
- The official runtime continues to inject the same existing Memory gateway.

No second conversation gateway, productive wiring, writer, adapter, memory gateway, authorization authority, or persistence route is introduced.

## Source-neutral conversational semantics

The historical Curiosity/Preference path keeps its existing preference wording.

For an already-certified write request whose `learning_category` is not `USER_PREFERENCE`, `_governed_learning_turn(...)` now uses source-neutral "aprendizaje" wording. This prevents a `STABLE_KNOWLEDGE` request from being conversationally represented as a preference while leaving the historical route backward compatible.

This distinction is presentation-only. It does not create a new category, authority, materializer, adapter, or write route.

## Preserved prohibitions

G10 does not:

- call G6/G7/G8 again;
- re-run human approval;
- recreate a materialization proposal;
- call `GovernedMemoryWriteAdapterFoundation` from the new seam;
- fabricate `PreferenceCandidate`, `preference_candidate_id`, `learning_kind`, or `CuriosityLearningKind.PREFERENCE` for source-neutral lineage;
- instantiate `OfficialMemoryGateway` inside the conversation gateway;
- add background work or silent learning;
- alter governed Memory persistence semantics.

## Validation performed in the delivery environment

Focused G10 contract:

- **5 passed**.

Combined regression block covering G10 + G9 + historical productive governed-learning wiring:

- **19 passed**.

The delivery environment does not provide Ruff, so final certification remains local and must use the project-mandated sequence:

`python scripts/generate_quality_baseline.py`

`ruff check .`

`pytest -q`

## Certification boundary

This SURGICAL GREEN is implemented but is not declared locally certified until the user runs the mandatory full validation and reports Ruff clean plus the full pytest suite without regressions.
