# ROBY XI.2 — Long-Horizon Investigation Reasoning Reentry Recording — Contract RED

Status: RED.

Expected production module (intentionally absent):
`app.governed_long_horizon_investigation_reasoning_reentry_recording`.

Expected public surfaces:
- `GovernedInvestigationReasoningReentryRecordingStatus`
- `GovernedInvestigationReasoningReentryRecordingResult`
- `GovernedLongHorizonInvestigationReasoningReentryRecordingV1`

The bridge consumes one exact admitted evidence result and a timezone-aware `now`. It may
invoke the existing `GovernedLevel2ReasoningReentryFoundationV1.reenter(...)` at most once,
then the existing `GovernedMultiStepInvestigationEpisodeBoundaryV1.record_reentry(...)` at
most once. It must preserve exact envelope, reentry and episode state/transition lineage.

Valid successful outcomes are either first-reentry `AWAITING_REQUIREMENT` continuation or
second-reentry mandatory `CLOSED/BUDGET_EXHAUSTED`. It must not create R2, invoke Planning,
execute capabilities, retry, persist, write Memory/World Model, ask questions, emit
conversation, or start background work.
