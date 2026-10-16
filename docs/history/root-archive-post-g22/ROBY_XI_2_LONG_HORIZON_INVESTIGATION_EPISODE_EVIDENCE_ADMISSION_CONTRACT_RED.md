# ROBY XI.2 — Long-Horizon Investigation
## Existing Acquired Evidence Envelope → Governed Episode Evidence Admission
### Contract RED

Status: RED — production adapter intentionally missing.

## Required public surface

Expected module:
`app.governed_long_horizon_investigation_episode_evidence_admission`

Expected public symbols:

- `GovernedInvestigationEpisodeEvidenceAdmissionStatus`
- `GovernedInvestigationEpisodeEvidenceAdmissionResult`
- `GovernedLongHorizonInvestigationEpisodeEvidenceAdmissionV1`

Expected productive method:

`consume(execution_result, checkpoint)`

## Required semantics

Only an exact long-horizon execution result with status `ACQUIRED`, a non-null exact
`GovernedAcquiredEvidenceEnvelope`, and matching checkpoint/thread/episode/reasoning/
requirement/source/snapshot lineage may reach episode admission.

The checkpoint must represent one unambiguous pre-acquisition episode state (`OPEN` step 1
or `READY_FOR_PLANNING` step 2). The adapter must project that same episode identity into
`GovernedInvestigationEpisodeState`, then pass the exact envelope object to the existing
`GovernedMultiStepInvestigationEpisodeBoundaryV1.record_acquisition` at most once.

Success requires the existing boundary to return `CONTINUE_ALLOWED` with status
`AWAITING_REENTRY`. The exact transition and resulting state are preserved. Only then may
`eligible_for_existing_reasoning_reentry` be true.

Non-acquired results, lineage mismatch, ambiguous checkpoint state, duplicate lineage,
boundary exception or unexpected transition fail closed without Reasoning.

## Forbidden semantics

No `GovernedMultiStepInvestigationExecutionReentryV1`, execution gateway, Planning,
Authorization, reasoning gateway/re-entry, EvidenceRegistry write, Memory, World Model,
retry, loop, persistence, question creation, conversation, background process, new episode
identity or truth establishment.
