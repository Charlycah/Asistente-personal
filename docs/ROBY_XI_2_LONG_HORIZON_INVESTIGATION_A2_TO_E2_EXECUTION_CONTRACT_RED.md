# ROBY XI.2 — Long-Horizon A2 → Existing E2 Execution Re-entry Contract RED

Expected production module (intentionally absent in RED):
`app.governed_long_horizon_investigation_e2_execution_reentry`

Expected public surfaces:
- `GovernedInvestigationE2ExecutionAdmissionStatus`
- `GovernedInvestigationE2ExecutionAdmissionResult`
- `GovernedLongHorizonInvestigationE2ExecutionReentryV1`

Productive method:
`consume(authorization_result, *, now)` where `authorization_result` is the exact
`GovernedInvestigationA2AuthorizationAdmissionResult`.

Frozen semantics:
1. Only exact `AUTHORIZED + MAY_INITIATE + eligible_for_existing_execution` A2 admission
   products may enter.
2. The exact historical `authorization_reentry` must be present and preserve step 2, one
   remaining acquisition, exact episode/R2/P2/A2/source/snapshot lineage and the exact planning
   continuation/state lineage.
3. The adapter delegates only to the existing
   `GovernedMultiStepInvestigationExecutionReentryV1` and invokes it at most once with the exact
   `authorization_result.authorization_reentry` object and exact caller-supplied `now`.
4. The returned canonical `GovernedInvestigationExecutionReentryResult` is preserved exactly.
5. `ACQUIRED` is trusted only with an exact acquired evidence envelope, one execution call, one
   episode acquisition record, `AWAITING_REENTRY`, zero remaining acquisitions and exact
   A2/P2/R2/source/snapshot lineage.
6. Only that recorded acquired E2 may expose
   `eligible_for_existing_reasoning_reentry=True`.
7. Canonical non-acquired `STOPPED`/`REVIEW_REQUIRED` outcomes never become reasoning-eligible.
8. Any exception or structural lineage mismatch is fail-closed `REVIEW_REQUIRED` with no retry.
9. No direct Level-2 gateway call, no generic long-horizon execution bridge, no separate episode
   admission, no Reasoning re-entry/closure, Planning, Authorization, requirement production,
   persistence, Memory/World Model mutation, Curiosity, Conversation or background work.
