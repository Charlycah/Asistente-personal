# Post-M409.1 — Governed Multi-Step Investigation A2 → Level 2 Read-Only Execution E2 Productive Re-entry v1

Status: IMPLEMENTED — pending official Ruff + full pytest certification.

## Productive path
valid A2 (`eligible_for_existing_execution=True`)
→ existing `GovernedLevel2ReadOnlyExecutionGatewayV1`
→ one E2 attempt
→ exact R2/P2/A2/source/snapshot lineage validation
→ existing `GovernedMultiStepInvestigationEpisodeBoundaryV1.record_acquisition`
→ if ACQUIRED: second budget slot consumed, episode `AWAITING_REENTRY`,
  `eligible_for_reasoning_reentry=True`
→ STOP.

## Governance
No execution authority is added. The bridge neither plans nor authorizes. It does not invoke
Reasoning Re-entry #2. The existing gateway remains constrained to local/internal read-only
evidence; device/network/state-changing execution is not widened.

## Fail closed
Execution is attempted at most once. FAILED, UNAVAILABLE, DENIED, REVIEW, gateway exception,
lineage mismatch, or E1 reuse cannot trigger retry, fallback, replanning, reauthorization,
another capability, or reasoning.

## Episode semantics
Only a valid ACQUIRED E2 is recorded as the second acquisition and leaves the episode
awaiting its second reasoning re-entry with `remaining_acquisitions == 0`. Closure remains
the responsibility of the already-certified `record_reentry` boundary after re-entry #2.

## Validation
Focused tests cover one-shot gateway use, E2 uniqueness and lineage, second-slot consumption,
reasoning eligibility without reasoning invocation, non-eligible A2, device denial, failed
read, gateway exception, E1 reuse, and absence of retry/side-effect/orchestrator authority.
Official certification remains `ruff check .` plus complete `pytest -q`.
