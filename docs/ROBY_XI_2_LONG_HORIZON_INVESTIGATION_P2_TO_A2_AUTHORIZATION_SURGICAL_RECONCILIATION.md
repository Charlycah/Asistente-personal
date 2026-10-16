# ROBY XI.2 — Long-Horizon Investigation P2 → A2 Authorization Surgical Reconciliation

## Baseline
Official incoming baseline: 13,630 PASS + Ruff clean (user-certified).

## Finding
The canonical step-2 Authorization re-entry owner already exists and is directly compatible
with the exact P2 Planning re-entry result emitted by the certified long-horizon R2 → P2
Planning block:

- `GovernedLongHorizonInvestigationP2PlanningReentryV1` preserves the exact historical
  `GovernedInvestigationPlanningReentryResult` in `result.planning_reentry`.
- `GovernedMultiStepInvestigationAuthorizationReentryV1.consume(...)` already accepts exactly
  `GovernedInvestigationPlanningReentryResult`.
- That historical owner already validates `PLANNED`, `PLANNABLE`, authorization eligibility,
  step 2, one remaining acquisition, and the presence of the exact planning product before
  invoking Authorization.
- It delegates to the existing `GovernedIndependenceAuthorizationBoundaryV1` exactly once,
  then uses the existing Authorization Productive Consumption surface.
- It preserves R2/P2/source/snapshot lineage, rejects reuse of a prior episode authorization
  id, and exposes execution eligibility only for `MAY_INITIATE`.

Therefore there is no architectural gap in Authorization itself and no second authorization
boundary is needed. The remaining long-horizon gap is only governed wiring from the exact
P2 admission product into that existing A2 owner while retaining thread/checkpoint/originating
reasoning lineage.

## Correct cut
`exact canonical P2 + eligible_for_existing_authorization`
→ validate exact long-horizon P2 admission and historical P2 re-entry identity/lineage
→ existing `GovernedMultiStepInvestigationAuthorizationReentryV1.consume(exact_P2)` once
→ preserve exact existing A2 re-entry result and authorization product
→ expose existing Execution eligibility only for `MAY_INITIATE`
→ STOP before E2 Execution.

## Why not reuse the earlier generic long-horizon Authorization adapter
`governed_long_horizon_investigation_evidence_authorization` is the adapter for the earlier
resume → existing evidence-acquisition-planning path. The current product is already the
specialized governed step-2 Planning re-entry result expected by the certified A2 owner.
Routing P2 through the generic adapter would bypass the step-2 invariants and duplicate
Authorization wiring.

## Required fail-closed rules
The bridge must reject before Authorization when the P2 admission is not `PLANNED`, is not
`eligible_for_existing_authorization`, lacks the exact historical `planning_reentry`, is not
canonical `PLANNABLE`, is not step 2 with one acquisition remaining, or breaks
requirement/plan/episode/source/snapshot lineage.

The exact `planning_result.planning_reentry` object is the only object that may be forwarded
to the existing A2 owner, at most once.

Once invoked, any exception, unexpected owner status, missing authorization product, reused
or mismatched R2/P2/A2/source/snapshot lineage, or mismatch between the returned A2 and the
exact P2 is `REVIEW_REQUIRED`. No retry is allowed.

`MAY_INITIATE` alone may expose `eligible_for_existing_execution=True`. `MUST_ASK` and
`MUST_ABSTAIN` remain valid Authorization outcomes but are never execution-eligible.

## Hard boundary
No new Authorization authority; no direct call to
`GovernedIndependenceAuthorizationBoundaryV1` from the long-horizon bridge; no reuse of the
earlier generic Authorization bridge; no Execution Gateway invocation, E2 acquisition,
Reasoning, Planning, requirement rewriting, episode mutation, retry, Memory/World Model
mutation, Curiosity, Conversation, networking, subprocess, scheduler, persistence or
background process.

## Next residual
Only after this cut is GREEN and certified:
`exact A2 + eligible_for_existing_execution → surgical reconciliation of existing E2 execution re-entry`.
