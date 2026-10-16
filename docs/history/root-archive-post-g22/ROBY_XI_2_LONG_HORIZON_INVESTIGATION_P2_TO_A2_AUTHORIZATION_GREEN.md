# ROBY XI.2 — Long-Horizon Investigation exact P2 → Existing A2 Authorization Re-entry GREEN

## Certified incoming baseline
13,630 PASS + Ruff clean (user-certified).

## Implemented cut
`exact canonical P2 + eligible_for_existing_authorization`
→ `GovernedLongHorizonInvestigationA2AuthorizationReentryV1`
→ existing `GovernedMultiStepInvestigationAuthorizationReentryV1.consume(exact P2)`
→ exact canonical A2 Authorization re-entry result
→ STOP before E2 Execution.

## Canonical ownership
No Authorization authority was added. The bridge delegates only to the existing step-2
owner `GovernedMultiStepInvestigationAuthorizationReentryV1`, which remains subordinate to
`GovernedIndependenceAuthorizationBoundaryV1`. The long-horizon adapter does not invoke the
Authorization boundary directly and does not reuse the earlier generic long-horizon
Authorization adapter.

## P2 admission invariants
Authorization is not invoked unless the incoming long-horizon Planning result is exactly
`PLANNED`, exposes `eligible_for_existing_authorization=True`, preserves a non-null exact
historical `planning_reentry`, is canonical `PLANNABLE`, step 2, and has one acquisition
remaining. Episode, R2, P2, source-reference, world-snapshot, continuation, requirement and
planning-product lineage must all remain coherent.

## A2 invariants
The exact `planning_result.planning_reentry` object is forwarded once. A successful bridge
result requires the existing owner to return canonical `AUTHORIZED`, the same P2 object,
one Authorization invocation, an exact non-null Authorization productive-consumption
product, a new A2 authorization id, and exact R2/P2/source/snapshot/episode lineage.

The exact returned `GovernedInvestigationAuthorizationReentryResult` and its exact
`authorization_product` are preserved by identity. `MAY_INITIATE` alone may expose
`eligible_for_existing_execution=True`; `MUST_ASK` and `MUST_ABSTAIN` remain valid A2
outcomes but do not become execution-eligible.

## Fail-closed behavior
Invalid P2 admission fails before Authorization as `NOT_ELIGIBLE`. Existing-owner
exceptions, unexpected non-`AUTHORIZED` output, missing product, reused A2, or any returned
lineage mismatch become `REVIEW_REQUIRED`. No retry is permitted.

## Hard stop
This GREEN does not invoke E2 Execution, Reasoning or Planning; does not rewrite R2 or
modify episode state; does not mutate Memory or World Model; and does not start background
work. It stops after exposing eligibility for the separate future E2 block.

## Tests
Functional GREEN coverage verifies exact one-shot P2 forwarding, exact A2/product
preservation, `MAY_INITIATE`-only E2 eligibility, preservation of `MUST_ASK` and
`MUST_ABSTAIN`, pre-Authorization fail-closed behavior, owner-failure review behavior,
returned-lineage validation, no retry, and the hard stop before E2.

## Next residual
`exact canonical A2 + eligible_for_existing_execution`
→ surgical reconciliation against the existing E2 Execution re-entry path.
