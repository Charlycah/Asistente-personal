# Post-M409.1 — Governed Multi-Step Investigation P2 → Independence Authorization A2 Productive Re-entry v1

Status: IMPLEMENTED — pending official Ruff + full pytest certification.

## Purpose
Take one valid step-2 Planning Re-entry product P2 and present it exactly once to the
already-certified Independence Authorization Boundary, then expose A2 through the existing
Authorization Productive Consumption surface.

## Productive path
valid step-2 Planning Re-entry (`eligible_for_authorization=True`)
→ exact P2
→ existing `GovernedIndependenceAuthorizationBoundaryV1`
→ A2
→ existing `GovernedIndependenceAuthorizationProductiveConsumptionV1`
→ `eligible_for_existing_execution=True` only for `MAY_INITIATE`
→ STOP.

## Authority and lineage
No authorization authority is added. A2 must preserve the exact requirement/plan/source/
snapshot lineage of R2/P2 and must not reuse any authorization id already consumed by the
episode. Episode state remains unchanged until a later acquired E2 is recorded by the
existing episode boundary.

## Fail-closed rules
Non-eligible or non-PLANNABLE P2 never invokes Authorization. Authorization exceptions
perform one failed invocation and no retry. Reused A1 or lineage mismatch produces review.
`MUST_ASK` and `MUST_ABSTAIN` are preserved and never promoted to execution eligibility.

## Hard boundaries
No Execution Gateway invocation, E2 acquisition, capability invocation, reasoning re-entry,
Curiosity, Conversation, Memory, Android, networking, subprocess, scheduler, retry,
fallback, state-changing action, or background loop is introduced.

## Validation
The new architecture/semantic tests cover one-call Authorization, exact A2 lineage, new-A2
identity, MAY/MUST_ASK/MUST_ABSTAIN gating, non-eligible P2, failure behavior, episode
immutability, and absence of downstream execution/side-effect authority. Official
certification remains `ruff check .` plus complete `pytest -q`.
