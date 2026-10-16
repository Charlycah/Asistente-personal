# ROBY XI.2 — Long-Horizon R2 → Existing P2 Planning Re-entry Contract RED

Expected production module (intentionally absent in RED):
`app.governed_long_horizon_investigation_p2_planning_reentry`

Expected public surfaces:
- `GovernedInvestigationP2PlanningAdmissionStatus`
- `GovernedInvestigationP2PlanningAdmissionResult`
- `GovernedLongHorizonInvestigationP2PlanningReentryV1`

Productive method:
`consume(admission)` where `admission` is the exact
`GovernedInvestigationReassessmentRequirementAdmissionResult`.

Frozen semantics:
1. Only exact `ADMITTED + eligible_for_existing_planning` RR1→R2 products may enter.
2. Exact `source_requirement`, `continuation`, and `resulting_episode_state` identity and
   episode/source/snapshot/step/budget lineage must be preserved.
3. The adapter delegates only to the existing
   `GovernedMultiStepInvestigationPlanningReentryV1` and invokes it at most once with the
   exact `admission.continuation` object.
4. The returned canonical `GovernedInvestigationPlanningReentryResult` is preserved exactly.
5. Success requires canonical `PLANNED` plus exact R2/P2/source/snapshot/episode lineage and
   a new P2 distinct from prior episode plans.
6. Authorization eligibility is derived only from the existing Planning re-entry result and
   only when P2 is `PLANNABLE`.
7. Non-PLANNABLE P2 is preserved but never Authorization-eligible.
8. Any exception, unexpected status, or lineage mismatch is fail-closed REVIEW with no retry.
9. No Authorization, Execution, Reasoning, requirement production, episode mutation,
   persistence, Curiosity, Conversation, networking or background work.
