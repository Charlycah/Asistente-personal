# ROBY XI.2 — Long-Horizon Investigation exact R2 → Existing P2 Planning Re-entry GREEN

## Certified incoming baseline
13,617 PASS + Ruff clean (user-certified).

## Implemented cut
`exact admitted R2 / READY_FOR_PLANNING`
→ `GovernedLongHorizonInvestigationP2PlanningReentryV1`
→ existing `GovernedMultiStepInvestigationPlanningReentryV1.consume(exact continuation)`
→ exact canonical P2 Planning re-entry result
→ STOP before A2 Authorization.

## Canonical ownership
No Planning authority was added. The bridge delegates only to the existing step-2 owner
`GovernedMultiStepInvestigationPlanningReentryV1`; that owner remains subordinate to the
canonical `planning_foundation` capability. The long-horizon adapter does not call
`GovernedEvidenceAcquisitionProductiveConsumptionV1` or an Evidence Acquisition planner
directly.

## Admission invariants
Planning is not invoked unless the incoming reassessment requirement admission is exactly
`ADMITTED`, planning-eligible, and preserves the same non-null R2, productive continuation,
and resulting episode state. The continuation and state must be
`CONTINUE_ALLOWED / READY_FOR_PLANNING`, step 2, with one acquisition remaining, and must
preserve episode, requirement, source-reference, and world-snapshot lineage.

## P2 invariants
The exact `admission.continuation` object is forwarded once. A successful bridge result
requires the existing owner to return canonical `PLANNED`, the same continuation, exact
R2/source/snapshot/episode lineage, a P2 plan ID not already present in the episode, and a
planning status identical across the existing planning product/report/re-entry result.

`PLANNABLE` is the only status that may expose
`eligible_for_existing_authorization=True`. A valid canonical non-PLANNABLE P2 remains a
Planning result but cannot advance to A2.

## Fail-closed behavior
Invalid admission fails before Planning as `NOT_ELIGIBLE`. Existing-owner exceptions,
unexpected non-PLANNED output, or post-Planning lineage mismatch become
`REVIEW_REQUIRED`. No retry is permitted.

## Hard stop
This GREEN does not invoke Authorization, Execution, or Reasoning; does not rewrite R2 or
modify episode state; does not mutate Memory or World Model; and does not start background
work. It stops after exposing eligibility for the separate future A2 block.

## Tests
Functional GREEN coverage verifies exact one-shot continuation forwarding, exact P2
preservation, PLANNABLE-only A2 eligibility, non-PLANNABLE preservation, pre-Planning
fail-closed behavior, owner-failure review behavior, and the hard stop before later
capabilities.

## Next residual
`exact canonical P2 + eligible_for_existing_authorization`
→ surgical reconciliation against the existing A2 Authorization re-entry owner.
