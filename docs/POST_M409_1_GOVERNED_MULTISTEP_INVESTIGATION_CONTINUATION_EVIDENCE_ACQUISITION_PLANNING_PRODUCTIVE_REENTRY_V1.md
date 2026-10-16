# Post-M409.1 — Governed Multi-Step Investigation Continuation → Evidence Acquisition Planning Productive Re-entry v1

Status: IMPLEMENTED — pending official Ruff + full pytest certification.

## Purpose
Take one certified productive continuation at step 2 and present its exact governed R2 to
the already-existing Evidence Acquisition Planning productive surface exactly once.

## Productive path
productive continuation (`eligible_for_existing_planning=True`)
→ exact `DiscriminatingEvidenceRequirement` R2
→ existing `GovernedEvidenceAcquisitionProductiveConsumptionV1`
→ new Evidence Acquisition Planning product P2
→ `eligible_for_authorization` only when P2 is `PLANNABLE`
→ STOP.

## Authority and reuse
Planning remains `planning_foundation`. The bridge does not create another planner, does
not rewrite R2, does not mutate episode state, and does not register P2 into the episode
before an actual acquired E2 is later recorded by the certified episode boundary.

## Fail-closed rules
Non-eligible continuation never invokes Planning. Planning failure performs no retry.
Source/requirement/snapshot mismatch and reuse of a prior episode plan produce review.
`AMBIGUOUS`, `PARTIALLY_PLANNABLE`, and `NO_CAPABILITY_AVAILABLE` Planning products are
preserved but are not promoted to Authorization eligibility.

## Hard boundaries
No Authorization, Productive Authorization, capability execution, reasoning, Curiosity,
Conversation, Memory, Android, networking, subprocess, scheduler, retry, fallback, or
background loop is introduced.

## Validation
The new architecture/semantic tests cover exact R2 preservation, one-call Planning,
new-P2 lineage, planning-status gating, failure behavior, episode immutability, and absence
of downstream authority/execution calls. Official certification remains `ruff check .`
plus complete `pytest -q`.
