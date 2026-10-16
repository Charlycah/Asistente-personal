# Post-M409.1 — Governed Multi-Step Investigation E2 → Reasoning Re-entry #2 / Mandatory Episode Closure v1

Status: IMPLEMENTED — pending official Ruff + full pytest certification.

## Purpose
Consume one valid acquired-and-recorded E2, re-enter the already-existing governed reasoning
surface exactly once, then submit RR2 to the already-existing Episode Boundary for mandatory
fixed-budget closure.

## Productive path
valid E2 (`eligible_for_reasoning_reentry=True`, episode `AWAITING_REENTRY`, budget 0)
→ existing `GovernedLevel2ReasoningReentryFoundationV1.reenter(E2)`
→ RR2
→ exact E2/A2/P2/R2/source/snapshot lineage validation
→ existing `GovernedMultiStepInvestigationEpisodeBoundaryV1.record_reentry`
→ `STOP_REQUIRED + CLOSED + BUDGET_EXHAUSTED + remaining_acquisitions=0`
→ STOP.

## Authority
No reasoning authority, episode authority, orchestrator, runner, or third-step authority is
introduced. Governed Reasoning remains the only reasoning authority and the Episode Boundary
remains the lifecycle authority.

## Mandatory closure
RR2 must be new relative to RR1 and may be attempted at most once. If the Episode Boundary
does not return the certified terminal state, the bridge returns review instead of accepting
continuation. The closure product exposes no Planning, Authorization, Execution, Reasoning
Re-entry, Curiosity, Conversation, Memory, retry, or background eligibility.

## Fail closed
Non-eligible E2 does not invoke Reasoning. Reasoning exceptions, non-REEVALUATED products,
RR1 reuse, lineage mismatches, snapshot/source mismatch, or nonterminal Episode Boundary
results produce review and cannot create R3/P3/A3/E3 or retries.

## Validation
Ten new architecture/semantic tests cover successful one-shot RR2 closure, complete lineage,
RR2 uniqueness, terminal eligibility suppression, non-eligible E2, reasoning failure, RR1
reuse, rejection of nonterminal boundary results, and absence of third-step/side-effect paths.
Official certification remains `ruff check .` plus complete `pytest -q`.
