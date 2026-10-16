# ROBY XI.2 — Long-Horizon Investigation R2 → P2 Planning Surgical Reconciliation

## Baseline
Official incoming baseline: 13,617 PASS + Ruff clean (user-certified).

## Finding
The canonical step-2 Planning owner already exists and is directly compatible with the
productive continuation emitted by the certified RR1 reassessment → R2 requirement
admission block:

- `GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1` preserves the exact
  admitted R2 in `result.source_requirement` and the exact productive episode continuation
  in `result.continuation`.
- `GovernedMultiStepInvestigationPlanningReentryV1.consume(...)` already accepts exactly
  `GovernedMultiStepInvestigationProductiveContinuation`.
- That historical owner already enforces `READY_FOR_PLANNING`, step 2, one remaining
  acquisition, exact R2/source/snapshot lineage, one Planning invocation, new P2 identity,
  and authorization eligibility only for `PLANNABLE`.

Therefore there is no architectural gap in Planning itself and no second planner is needed.
The remaining long-horizon gap is only governed wiring from the exact R2 admission product
into that existing P2 Planning re-entry owner while preserving long-horizon lineage.

## Correct cut
`exact admitted R2 result`
→ validate exact admission/continuation/state/R2 identity and lineage
→ existing `GovernedMultiStepInvestigationPlanningReentryV1.consume(exact_continuation)` once
→ preserve exact existing P2 re-entry result
→ expose existing Authorization eligibility only when P2 is `PLANNABLE`
→ STOP before Authorization.

## Why not reuse Resume → Existing Planning
`governed_long_horizon_investigation_evidence_planning` is a different adapter for a resume
admission product. The R2 block already owns a canonical productive continuation at step 2.
Routing it through Resume would discard/reshape the stronger episode continuation contract
and would duplicate the already-existing P2 re-entry path.

## Required fail-closed rules
The bridge must reject before Planning when the admission is not `ADMITTED`, is not planning
eligible, lacks exact R2/continuation/state identity, is not `READY_FOR_PLANNING` at step 2
with one acquisition remaining, or breaks episode/source/snapshot/requirement lineage.

Once invoked, any exception, unexpected non-PLANNED result, or returned lineage mismatch is
`REVIEW_REQUIRED`. No retry is allowed.

A valid non-PLANNABLE Planning product may still be preserved as a Planning result, but it
must not be promoted to Authorization eligibility. Only canonical `PLANNABLE` P2 may expose
`eligible_for_existing_authorization=True`.

## Hard boundary
No new planner; no direct `planning_foundation` call; no direct
`GovernedEvidenceAcquisitionProductiveConsumptionV1` call from the long-horizon adapter;
no Authorization, Execution, Reasoning, requirement rewriting, episode mutation, retry,
Memory/World Model mutation, Curiosity, Conversation, networking, subprocess, scheduler or
background process.

## Next residual
Only after this cut is GREEN and certified:
`exact P2 + eligible_for_existing_authorization → existing A2 Authorization re-entry`.
