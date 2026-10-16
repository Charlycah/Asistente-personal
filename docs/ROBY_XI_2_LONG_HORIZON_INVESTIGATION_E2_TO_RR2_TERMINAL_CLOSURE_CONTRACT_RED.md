# ROBY XI.2 — RED Contract: exact recorded E2 → RR2 terminal closure

Expected module (deliberately absent in RED):
`app.governed_long_horizon_investigation_rr2_terminal_closure`

Expected public API:
- `GovernedInvestigationRR2TerminalClosureStatus`
- `GovernedInvestigationRR2TerminalClosureResult`
- `GovernedLongHorizonInvestigationRR2TerminalClosureV1`

Frozen contract:
1. Accept only exact ACQUIRED E2 with `eligible_for_existing_reasoning_reentry=True`.
2. Preserve exact `execution_reentry`, evidence envelope, resulting episode state and E2/A2/P2/R2/source/snapshot/episode lineage.
3. Delegate only to existing `GovernedMultiStepInvestigationReasoningClosureV1`, exactly once, forwarding exact `e2_result.execution_reentry` and exact `now`.
4. Preserve exact `GovernedInvestigationReasoningClosureResult` returned by the canonical owner.
5. Success only for canonical CLOSED with exactly one RR2 invocation and one episode record.
6. Terminal state must be STOP_REQUIRED/CLOSED/BUDGET_EXHAUSTED/remaining_acquisitions=0 and RR2 must be new relative to prior reentries.
7. Any ineligibility, exception, unexpected status, identity mismatch or lineage mismatch fails closed; no retry.
8. Never expose R3/P3/A3/E3, new requirement, curiosity, persistence, Memory/World Model mutation, conversation or background work.
