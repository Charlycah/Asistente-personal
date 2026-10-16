# ROBY XI.2 — CAP-11 Source-Neutral One-Step Productive Continuation

Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION**.

Starting owner-certified baseline: **12,492 PASS · 0 FAIL · Ruff clean**.

## Productive seam

One already-admitted governed R(N+1) can now be handed from the productive
CAP-17 evidence path into a source-neutral application coordinator.

The coordinator composes only existing owners:

1. `GovernedMultiStepInvestigationPlanningReentryV1`
2. `GovernedMultiStepInvestigationAuthorizationReentryV1`
3. `GovernedMultiStepInvestigationExecutionReentryV1`
4. `GovernedMultiStepInvestigationReasoningClosureV1`

The existing `GovernedIndependenceAuthorizationBoundaryV1` remains the sole
initiation-policy authority.

`MAY_INITIATE` may advance to the existing read-only execution gateway.
`MUST_ASK`, `MUST_ABSTAIN`, `REVIEW_REQUIRED`, planning failure, execution failure
or reasoning failure stop the one-step continuation without escalation.

The coordinator never derives R(N+2), never recurses, never starts background work
and never touches Memory or World Model.

Invariant:

**ONE ADMITTED NEXT REQUIREMENT → AT MOST ONE GOVERNED ACQUISITION/REASONING STEP → STOP**
