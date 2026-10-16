# Post-M409.1 — Governed Multi-Step Investigation Productive Continuation v1

Status: IMPLEMENTED — pending official Ruff + full pytest certification.

## Purpose
Expose one already-governed episode continuation decision productively, preserving the
supplied R2 requirement and episode lineage without performing any downstream step.

## Productive path
episode state (`AWAITING_REQUIREMENT`)
→ supplied governed `DiscriminatingEvidenceRequirement` R2
→ existing `GovernedMultiStepInvestigationEpisodeBoundaryV1.evaluate_continuation`
→ `CONTINUE_ALLOWED / STOP_REQUIRED / REVIEW_REQUIRED`
→ `eligible_for_existing_planning`
→ STOP.

## Authority
No authority is introduced. R2 remains a governed reasoning/discrimination product and
Planning remains `planning_foundation`. The productive surface does not create or rewrite
requirements and does not invoke Planning, authorization, execution, reasoning, Curiosity,
Conversation, Memory, Android, networking, subprocesses, schedulers, or background loops.

## Semantics
Only a valid `CONTINUE_ALLOWED` transition entering step 2 with exactly one remaining
acquisition sets `eligible_for_existing_planning=True`. This is not `MAY_INITIATE` and is
not execution authorization.

## Validation
Focused architecture/semantic validation covers valid continuation, requirement identity,
source/snapshot mismatch review, requirement reuse, missing requirement, closed episode,
absence of downstream authority calls, and non-operational defaults. Official certification
remains `ruff check .` plus complete `pytest -q`.
