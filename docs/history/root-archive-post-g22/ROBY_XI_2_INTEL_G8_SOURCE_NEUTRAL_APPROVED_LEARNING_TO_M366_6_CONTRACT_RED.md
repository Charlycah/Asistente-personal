# ROBY XI.2 — INTEL-G8 — CONTRACT RED

## Source of truth

This RED contract is based only on the locally certified INTEL-G7 GREEN CORRECTED
baseline:

- 14,098 tests passing
- Ruff clean
- zero known regressions

## Architectural purpose

INTEL-G8 freezes the minimal source-neutral seam from already-approved G7 learning
into the existing governed durable-materialization authority. It does not create a
new durable-memory system and it does not write Memory.

The frozen boundary is:

```text
G6 source-neutral M369 evaluation
        +
G7 explicit exact-linked approved learning evidence
        ↓
existing governed structural eligibility
        ↓
existing M366.6 consolidation/materialization authority
        ↓
GovernedMemoryMaterializationProposal
        ↓
STOP
```

## Contract obligations

1. Only an exact-linked G6 evaluation and G7 approved-learning evidence pair may
   enter the seam.
2. Stable knowledge reuses existing governed Reasoning to produce
   `StructuralEligibilityEvidence`.
3. Stable knowledge without valid structural eligibility remains
   `REVIEW_REQUIRED` and produces no proposal.
4. Non-durable scopes such as `SESSION` remain `REVIEW_REQUIRED` and produce no
   durable proposal.
5. A successful path reuses the existing
   `ApprovedLearningMemoryMaterializationProposalFoundation`, existing M366.6
   consolidation, and the existing `GovernedMemoryMaterializationProposal`.
6. The proposal is source-neutral: it preserves G6/G7 lineage and must not invent
   Curiosity or Preference provenance.
7. `LearningCategory.STABLE_KNOWLEDGE` is the canonical durable semantic category.
8. The proposal remains read-only; persistence is not performed.
9. The official Memory writer is not called.
10. No new Learning, Knowledge, Memory, materialization, runtime, or persistence
    authority may be introduced.

## Frozen source-neutral lineage

The successful proposal must preserve at least:

- G6 `learning_candidate_id`
- G6 `policy_candidate_id`
- G6 subject and proposed value
- G6 aggregate confidence
- G6 policy evidence IDs
- G6 evaluation fingerprint
- G7 approval ID and approval fingerprint
- G7 human response reference
- G7 approver and scope
- structural eligibility fingerprint and governed-reasoning lineage

Historical `preference_candidate_id` must not be fabricated for the source-neutral
path.

## STOP

INTEL-G8 ends at `GovernedMemoryMaterializationProposal`.

The following are explicitly out of scope:

- `GovernedMemoryWriteRequest`
- write adapter invocation
- `OfficialMemoryGateway` invocation
- Memory persistence
- productive runtime wiring
- automatic learning
- automatic consolidation
- background learning or research
- fake `PreferenceCandidate`
- fake Curiosity provenance
- second Learning/Knowledge/Memory/materialization authority

`APPROVED != MATERIALIZED`

`MATERIALIZATION PROPOSAL != PERSISTED`

The productive G8 module is intentionally absent in CONTRACT RED.
