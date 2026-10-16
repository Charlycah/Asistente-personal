# ROBY XI.2 — Long-Horizon Investigation
## Governed Episode Evidence Admission → Existing Governed Reasoning Reentry → Governed Episode Reentry Recording
### Surgical Reconciliation

Status: RECONCILED — production bridge intentionally absent (RED next).
Baseline: 13,594 PASS + Ruff clean, user-certified.

## Governing context
This block follows the root rules and CAP-11 master inventory. It deepens long-horizon
resumability without introducing a second planner, reasoning authority, episode authority,
evidence registry, executor, persistence owner, scheduler, or background worker.

ROBY remains private/personal and local-first. This block does not alter `config.json`,
credential material, distribution/commercial behavior, Memory, World Model, Learning,
Conversation, Curiosity, networking, Android/device execution, or Residential scope.

## Existing canonical owners
Two distinct existing owners are required and must remain distinct:

1. Reasoning re-entry:
   `GovernedLevel2ReasoningReentryFoundationV1.reenter(...)`
   - canonical authority: `governed_reasoning`;
   - registers the acquired envelope in the canonical evidence registry;
   - evidence kind remains `OBSERVATION` / `LEVEL2_ACQUIRED`;
   - metadata preserves `epistemic_role=observation_not_truth`;
   - one execution lineage may be reevaluated at most once;
   - no capability execution, retry, persistence, question, conversation, Memory or World Model mutation.

2. Episode lifecycle recording:
   `GovernedMultiStepInvestigationEpisodeBoundaryV1.record_reentry(...)`
   - existing episode/lifecycle owner under the planning-foundation boundary;
   - requires exact E/A/R/P/source/snapshot lineage;
   - first recorded reentry: `CONTINUE_ALLOWED + AWAITING_REQUIREMENT` with one acquisition remaining;
   - second recorded reentry: `STOP_REQUIRED + CLOSED + BUDGET_EXHAUSTED` with zero acquisitions remaining.

## Existing specialized closure is not the long-horizon bridge
`GovernedMultiStepInvestigationReasoningClosureV1` is already correct for the historical
step-2 E2 product, but it accepts `GovernedInvestigationExecutionReentryResult` and requires
step 2 / exhausted budget. It cannot consume the new long-horizon
`GovernedInvestigationEpisodeEvidenceAdmissionResult`, and it cannot represent the valid
first-acquisition `AWAITING_REQUIREMENT` outcome.

The new bridge therefore composes the two existing owners directly; it does not replace,
modify, or duplicate the specialized closure.

## Frozen productive cut
Input:
`GovernedInvestigationEpisodeEvidenceAdmissionResult`

It may cross into Reasoning only when all are true:
- admission status is `ADMITTED`;
- `eligible_for_existing_reasoning_reentry=True`;
- exact evidence envelope is present and `ACQUIRED`;
- exact resulting episode state is present and `AWAITING_REENTRY`;
- admission transition/state identity is preserved;
- episode/thread/checkpoint/requirement/source/snapshot lineage is internally consistent;
- the envelope execution/authorization/requirement/plan/source/snapshot lineage matches the admitted episode state.

Then, at most once:

`GovernedLevel2ReasoningReentryFoundationV1.reenter(admission.evidence_envelope, now=now)`

Only a canonical `REEVALUATED` product with exact envelope lineage may proceed. Then, at most once:

`GovernedMultiStepInvestigationEpisodeBoundaryV1.record_reentry(
    admission.resulting_episode_state,
    exact_reentry,
)`

The exact reentry result and exact canonical episode transition/state must be preserved.

## Valid terminal shapes for this bridge
The bridge must support both already-governed episode positions:

- RR1 / first acquisition recorded:
  `CONTINUE_ALLOWED + AWAITING_REQUIREMENT + remaining_acquisitions=1`.
  This only exposes that the episode awaits a separately governed requirement-resolution step.
  It must not create, infer, rewrite, or select R2 and must not invoke productive continuation or Planning.

- RR2 / second acquisition recorded:
  `STOP_REQUIRED + CLOSED + BUDGET_EXHAUSTED + remaining_acquisitions=0`.
  This is terminal and exposes no downstream execution/planning/reentry eligibility.

Any other transition shape fails closed as review.

## Important long-horizon residual discovered
After RR1, the episode is `AWAITING_REQUIREMENT`. The current Resume Admission surface is not
a safe substitute for producing R2: it rebinds an already-existing exact requirement and does
not create/derive a new discriminating requirement. Therefore this block must stop after
recording RR1. A later reconciliation must identify the existing governed source of the new
post-reevaluation discriminating requirement and how it reaches Productive Continuation and a
new passive checkpoint without replaying R1.

## Non-goals
No new EvidenceRegistry. No direct `.reason(...)` call. No direct capability execution. No
retry loop. No automatic R2 creation. No Planning/Authorization/Execution invocation. No
checkpoint persistence/update in this block. No Memory, World Model, Learning, Conversation,
Curiosity, networking, Android, subprocess, scheduler, or background process.

## Next residual after GREEN
If RR1: `Recorded RR1 / AWAITING_REQUIREMENT → exact governed post-reevaluation discriminating requirement → existing Productive Continuation / passive continuity` (must be surgically reconciled).

If RR2: terminal episode; no continuation residual from that episode.
