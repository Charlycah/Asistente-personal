# ROBY XI.2 — Surgical Reconciliation: exact recorded E2 → RR2 → terminal closure

Incoming certified baseline: **13,656 PASS + Ruff clean** (user-local certification).

## Governing finding

The canonical terminal owner already exists: `GovernedMultiStepInvestigationReasoningClosureV1` in `app/governed_multistep_investigation_reasoning_closure.py`.

It already consumes `GovernedInvestigationExecutionReentryResult`, invokes the existing `GovernedLevel2ReasoningReentryFoundationV1` at most once, records that exact RR2 through `GovernedMultiStepInvestigationEpisodeBoundaryV1.record_reentry(...)`, and accepts success only as `STOP_REQUIRED + CLOSED + BUDGET_EXHAUSTED + remaining_acquisitions=0`.

Therefore no second reasoning authority, no second episode authority, and no new terminal policy are required.

## Exact long-horizon gap

The certified E2 bridge returns `GovernedInvestigationE2ExecutionAdmissionResult`, while the historical closure owner consumes its preserved inner `execution_reentry`.

The only missing surface is a narrow long-horizon adapter:

`exact recorded E2 + eligible_for_existing_reasoning_reentry`
→ exact `e2_result.execution_reentry`
→ existing `GovernedMultiStepInvestigationReasoningClosureV1.consume(..., now=now)` exactly once
→ preserve exact canonical closure result
→ terminal stop.

## Mandatory eligibility

Before RR2 the adapter must require canonical ACQUIRED E2, exact inner execution-reentry identity, exact evidence/state identity, step 2, zero remaining acquisitions, AWAITING_REENTRY, consumed budget equal to max budget, and exact E2/A2/P2/R2/source/snapshot/episode lineage.

## Terminal invariant

Success is only canonical `CLOSED`, with one reasoning call, one episode record, a new RR2 not reused from RR1, and resulting state `CLOSED / BUDGET_EXHAUSTED / remaining_acquisitions=0`.

No R3, P3, A3, E3, requirement creation, curiosity, retry, persistence, Memory/World Model mutation, conversation, or background process may be exposed.
