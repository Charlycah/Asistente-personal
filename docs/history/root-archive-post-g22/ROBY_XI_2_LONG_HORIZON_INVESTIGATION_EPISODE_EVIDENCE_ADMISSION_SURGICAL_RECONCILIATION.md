# ROBY XI.2 — Long-Horizon Investigation
## Existing Acquired Evidence Envelope → Governed Episode Evidence Admission
### Surgical Reconciliation

Status: RECONCILED — RED contract permitted; production bridge intentionally absent.
Baseline entering this block: 13,582 PASS + Ruff clean (user-certified).

## 1. Governing documents consulted

This reconciliation follows the root `VISION.md`, `architecture_rules.md`,
`ESTADO_MAESTRO_INTEGRAL.md`, `INVENTARIO_COGNITIVO_INTEGRAL_ROBY_XI_2.md`,
`ROBY_XI_2_COGNITIVE_INVENTORY_RECONCILIATION_MASTER_GUIDE.md`, and
`ROBY_XI_2_MASTER_CAPABILITY_REGISTRY.md`.

The governing rules remain unchanged: ROBY is private, personal, non-commercial and
non-distributable; one canonical authority per capability; extend/integrate existing
owners before creating a new capability; evidence never becomes truth merely by being
observed; no `config.json` or credential-store change belongs to this block.

## 2. Exact current path already certified

Passive durable checkpoint
→ explicit governed resume candidate
→ exact Requirement rebinding / resume admission
→ existing evidence acquisition Planning
→ existing independence Authorization
→ existing Level-2 read-only Execution Gateway
→ exact `GovernedAcquiredEvidenceEnvelope`
→ STOP.

The current long-horizon execution result deliberately has
`records_episode_evidence=False` and `invokes_reasoning=False`.

## 3. Existing canonical owners

### Episode lifecycle/admission owner

`app.governed_multistep_investigation_episode.GovernedMultiStepInvestigationEpisodeBoundaryV1`

Its `record_acquisition(state, envelope)` is already the canonical mutation boundary for
admitting one execution lineage into the bounded investigation episode. It validates
requirement/source/snapshot lineage, unique plan/authorization/execution identity, stopping
conditions and budget. A valid acquired envelope transitions the episode to
`AWAITING_REENTRY`.

No new episode manager, investigation authority, state store or planner is permitted.

### Reasoning re-entry owner

`app.governed_level2_reasoning_reentry.GovernedLevel2ReasoningReentryFoundationV1`

It already converts one ACQUIRED Level-2 envelope into the canonical `EvidenceRegistry`,
marks the reference `LEVEL2_ACQUIRED / OBSERVATION`, preserves `observation_not_truth`, and
invokes the existing governed reasoning gateway at most once.

No second evidence registry or reasoning authority is permitted.

## 4. Why the historical execution-reentry bridge is not the owner for this cut

`GovernedMultiStepInvestigationExecutionReentryV1` is specialized to the historical
step-2 continuation path. Its input is `GovernedInvestigationAuthorizationReentryResult`;
it executes the gateway itself and expects the continuation state to already be the
step-2 state with one acquisition remaining.

The long-horizon path has already executed through the newly certified existing-execution
bridge and owns an exact acquired envelope. Reusing the historical bridge would execute a
second time and would require the wrong input lineage. It must not be used.

## 5. Hidden continuity constraint discovered

The passive checkpoint is the durable carrier of episode lineage across time. The later
Resume → Planning → Authorization → Execution products preserve checkpoint/thread/episode
IDs, but they do not carry a live `GovernedInvestigationEpisodeState` object.

Therefore episode admission must be explicitly bound to the exact checkpoint that sourced
the resumed chain. Requiring an unrelated live state would defeat long-horizon resumability;
constructing a new episode would break identity.

A checkpoint may only be projected back to the canonical episode state when its state is
unambiguous:

- `OPEN`: step 1, zero consumed acquisitions, one requirement, no plan/authorization/
  execution/reentry lineage yet.
- `READY_FOR_PLANNING`: step 2, one consumed acquisition, two requirements, and exactly one
  prior plan/authorization/execution/reentry lineage.

Other checkpoint states (`AWAITING_REENTRY`, `AWAITING_REQUIREMENT`, `CLOSED`,
`REVIEW_REQUIRED`) are not valid pre-acquisition states for this bridge and must fail closed.

This is compatibility validation, not a new episode authority.

## 6. Exact surgical cut

New narrow adapter only:

`GovernedInvestigationEvidenceExecutionResult(ACQUIRED)`
+ exact `GovernedPassiveInvestigationCheckpoint`
→ validate complete checkpoint/thread/episode/reasoning/requirement/source/snapshot lineage
→ project that checkpoint into its exact supported pre-acquisition
  `GovernedInvestigationEpisodeState`
→ call existing `GovernedMultiStepInvestigationEpisodeBoundaryV1.record_acquisition`
  exactly once with the exact existing `GovernedAcquiredEvidenceEnvelope`
→ require canonical transition `CONTINUE_ALLOWED + AWAITING_REENTRY`
→ expose the exact transition/resulting state
→ set only `eligible_for_existing_reasoning_reentry=True`
→ STOP.

## 7. Hard boundaries

This block must not:

- invoke Reasoning or `GovernedLevel2ReasoningReentryFoundationV1`;
- execute the capability gateway again;
- create a new episode ID;
- call Planning or Authorization;
- retry/fallback/loop;
- persist results;
- write Memory or World Model;
- create questions or conversation;
- establish truth;
- alter `config.json`, credentials or runtime configuration.

## 8. Why Reasoning Reentry is a separate next block

Episode admission mutates only the canonical investigation episode state. Reasoning re-entry
belongs to the canonical governed reasoning surface and performs a governed reasoning
evaluation. Combining both would hide two authority crossings inside one adapter and make a
successful acquisition automatically execute reasoning.

The master inventory requires the residual to be smaller than the feature name. Therefore
the next block after this one is frozen as:

**Governed Episode Evidence Admission → Existing Governed Reasoning Reentry → Governed Episode Reentry Recording**

That later block may call the existing reasoning re-entry owner at most once and then submit
the exact re-entry product to the existing episode boundary `record_reentry`, without
creating any third authority.
