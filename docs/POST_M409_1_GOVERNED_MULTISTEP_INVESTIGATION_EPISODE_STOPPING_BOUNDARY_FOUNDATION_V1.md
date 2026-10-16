# Post-M409.1 — Governed Multi-Step Investigation Episode / Stopping Boundary Foundation v1

Status: IMPLEMENTED — pending official Ruff + full pytest certification.

## Purpose
Represent one bounded Level 2 investigation episode as immutable state and decide only
whether one more product may proceed to the already-existing planning path or whether the
episode must stop/review.

## Authority
`PlanningFoundation` remains the only planning authority. The Foundation validates that
its snapshot remains read-only and that `planning_execution_authorized` is false. No
`InvestigationAuthority`, manager, runner, executor, planner or reasoner is introduced.

## Fixed v1 budget
`max_acquisitions = 2` is an architectural invariant. It is not configurable during the
episode and it is not capability metadata.

## Explicit transition path
episode start
→ acquisition #1 recorded
→ existing reasoning re-entry #1 recorded
→ optional new discriminating requirement R2
→ `CONTINUE_ALLOWED` only back to existing Planning
→ new authorization/execution lineage
→ acquisition #2 recorded
→ existing reasoning re-entry #2
→ `BUDGET_EXHAUSTED`
→ STOP.

Each call performs exactly one state transition. There is no internal loop.

## Stopping semantics
The boundary can stop/review for missing new requirement, authorization refusal, failed or
unavailable acquisition, broken/reused lineage, snapshot conflict, budget exhaustion or a
manual stop. Failed/unavailable acquisition does not consume a successful-acquisition slot
and never enables automatic retry.

## Hard boundaries
No capability invocation, reasoning execution, planning execution, persistence, Memory
Gateway, Conversation, Curiosity, Android, networking, subprocess, scheduler, retry,
fallback, state-changing action or background processing is introduced.

## Validation
Architecture/semantic tests cover the complete two-step state sequence, fixed budget,
single-use lineage, stopping conditions, snapshot continuity and absence of loop/execution
authority. Official certification remains `ruff check .` plus complete `pytest -q`.
