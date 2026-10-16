# ROBY XI.2 — Long-Horizon Investigation
## Existing Acquired Evidence Envelope → Governed Episode Evidence Admission
### GREEN

Status: GREEN implemented; local user certification pending.
Entering certified baseline: 13,582 PASS + Ruff clean.

## Productive cut implemented

`GovernedInvestigationEvidenceExecutionResult(ACQUIRED)` plus the exact
`GovernedPassiveInvestigationCheckpoint` now reaches only the existing canonical episode
owner:

`GovernedMultiStepInvestigationEpisodeBoundaryV1.record_acquisition(...)`.

The new adapter is
`GovernedLongHorizonInvestigationEpisodeEvidenceAdmissionV1` in
`app.governed_long_horizon_investigation_episode_evidence_admission`.

It validates checkpoint/thread/episode/originating-reasoning/requirement/source/snapshot
lineage, accepts only an unambiguous checkpoint projection (`OPEN` step 1 or
`READY_FOR_PLANNING` step 2), reconstructs the same episode identity, and forwards the
exact existing acquired-evidence envelope once.

## Success semantics

Success is only:

`CONTINUE_ALLOWED + AWAITING_REENTRY`.

The exact canonical transition and resulting episode state are preserved. Only then is
`eligible_for_existing_reasoning_reentry=True` exposed.

The adapter does not invoke reasoning. Evidence remains an observation and is not promoted
to truth by this admission step.

## Fail-closed semantics

The adapter does not invoke the episode boundary when the execution is not ACQUIRED, when
checkpoint/execution lineage differs, or when checkpoint state/shape is ambiguous.
Projection errors, boundary errors, and unexpected transitions become `REVIEW_REQUIRED`.
No retry or fallback is permitted.

## Preserved governance

No new episode authority, planner, authorization owner, execution gateway, EvidenceRegistry,
Memory writer, World Model writer or reasoning owner was introduced. `config.json`, runtime
configuration and credential stores are outside this block and remain untouched.

## Next residual

The next block remains separate:

**Governed Episode Evidence Admission → Existing Governed Reasoning Reentry → Governed Episode Reentry Recording**

That later block may cross the existing reasoning owner and then return the exact re-entry
product to the existing episode boundary. This GREEN stops before that crossing.
