# ROBY XI.2 — Long-Horizon P2 → Existing A2 Authorization Re-entry Contract RED

Expected production module (intentionally absent in RED):
`app.governed_long_horizon_investigation_a2_authorization_reentry`

Expected public surfaces:
- `GovernedInvestigationA2AuthorizationAdmissionStatus`
- `GovernedInvestigationA2AuthorizationAdmissionResult`
- `GovernedLongHorizonInvestigationA2AuthorizationReentryV1`

Productive method:
`consume(planning_result)` where `planning_result` is the exact
`GovernedInvestigationP2PlanningAdmissionResult`.

Frozen semantics:
1. Only exact `PLANNED + eligible_for_existing_authorization` P2 admission products may enter.
2. The exact historical `planning_reentry` must be present, canonical `PLANNABLE`, step 2,
   with exactly one acquisition remaining and exact episode/R2/P2/source/snapshot lineage.
3. The adapter delegates only to the existing
   `GovernedMultiStepInvestigationAuthorizationReentryV1` and invokes it at most once with
   the exact `planning_result.planning_reentry` object.
4. The returned canonical `GovernedInvestigationAuthorizationReentryResult` is preserved
   exactly.
5. A2 must preserve R2/P2/source/snapshot lineage and be new relative to prior episode
   authorization ids, as already enforced by the canonical A2 owner.
6. `MAY_INITIATE` alone may expose `eligible_for_existing_execution=True`.
7. `MUST_ASK` and `MUST_ABSTAIN` are preserved as Authorization outcomes but never become
   execution-eligible.
8. Any exception, unexpected status, missing product, or lineage mismatch is fail-closed
   `REVIEW_REQUIRED` with no retry.
9. No E2 Execution, Planning, Reasoning, requirement production, episode mutation,
   persistence, Memory/World Model mutation, Curiosity, Conversation, networking or
   background work.
