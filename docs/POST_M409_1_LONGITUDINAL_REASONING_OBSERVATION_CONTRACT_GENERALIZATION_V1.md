# Post-M409.1 — Longitudinal Reasoning Observation Contract Generalization v1

## Purpose

Generalize only the input representation consumed by the certified Governed
Longitudinal Reasoning Assessment Foundation. The longitudinal semantics, authority,
statuses, counts, comparability rules and no-power boundaries remain unchanged.

## Neutral observation contract

`GovernedReasoningAssessmentObservation` no longer stores complete
`GovernedReasoningQualityAssessment` and `GovernedEpistemicSufficiencyAssessment`
objects. It carries only the information actually required for cross-episode
assessment:

- reasoning-quality assessment ID and status;
- epistemic-sufficiency assessment ID and status;
- explicit `source_reference`;
- `world_snapshot_id` lineage;
- source fingerprints for both certified assessments;
- existing `governed_reasoning` authority plus read-only/consultative invariants.

The contract contains no timestamp, sequence, Memory, Learning, Event Bus or history
reader dependency.

## Live-assessment compatibility

`GovernedReasoningAssessmentObservation.from_assessments(...)` is the explicit adapter
for existing live assessment objects. Before projecting them it preserves the original
fail-closed checks:

- both sources retain `canonical_authority="governed_reasoning"`;
- both sources are read-only and consultative;
- Reasoning Quality names the supplied Sufficiency assessment exactly;
- source reference and world snapshot lineage match;
- both source fingerprints are present.

No report is recalculated or persisted.

## Why this generalization is required

The certified M203 reasoning-assessment event projection intentionally retains a
canonical projection of Quality/Sufficiency identity, status and provenance, not the
complete upstream Deepening/Discrimination/Update report graphs. Reconstructing full
assessment dataclasses from those events would fabricate fields and provenance.

The neutral observation contract allows both live certified assessments and a future
read-only admitted-event history reader to supply the same longitudinal semantic input
without false rehydration.

## Preserved semantics

The Foundation still derives only:

- `INSUFFICIENT_HISTORY`;
- `CONSISTENTLY_ADEQUATE`;
- `RECURRENT_LIMITATION`;
- `RECURRENT_REVIEW_REQUIRED`;
- `MIXED`.

A series still requires one explicit `source_reference`, unique Quality/Sufficiency
assessment IDs and deterministic ordering. `world_snapshot_id` values remain lineage,
not a temporal trend signal.

No score, probability, truth promotion, temporal improving/degrading claim, automatic
review, rerun, Reflection, Curiosity, Learning, Memory, persistence, adaptation,
Planning or Execution is added.

## Architecture boundary

- No modification to M203 Cognitive Event Bus.
- No history reader is implemented in this increment.
- No import from `core.governed_reasoning` to app-layer event projection/history code.
- No new authority, registry, repository or persistence surface.
- `governed_reasoning` remains the canonical authority.

## Validation target

Focused tests protect exact neutral projection, live-assessment pairing, source/snapshot
lineage, fingerprints, enum status integrity, authority/read-only invariants, direct
Foundation consumption, no temporal/persistence fields and no Event Bus/Memory/history
reader import dependency.
