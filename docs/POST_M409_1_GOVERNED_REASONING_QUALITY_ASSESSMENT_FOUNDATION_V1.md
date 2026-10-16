# Post-M409.1 — Governed Reasoning Quality Assessment Foundation v1

## Purpose

Add a pure, read-only assessment over one coherent governed epistemic reasoning episode. The foundation evaluates whether the episode result is adequate, explicitly limited, or requires review without rerunning or correcting reasoning.

## Reused inputs

- `GovernedHypothesisDeepeningReport` — required episode anchor.
- `GovernedEpistemicSufficiencyAssessment` — required contextual epistemic result.
- `GovernedHypothesisUpdateSemanticsReport` — optional, when the sufficiency lineage references it.
- `GovernedMultiHypothesisDiscriminationReport` — optional, when the sufficiency lineage references it.

The episode is identified by coherent source/snapshot lineage. No Episode Manager, store, registry, or authority is introduced.

## Status semantics

- `ADEQUATE`: lineage is coherent and the final epistemic state is contextually sufficient. Adequate does not mean true, correct, certain, or final.
- `LIMITED`: the episode is valid but carries explicit epistemic insufficiency. Insufficiency is not treated as reasoning failure.
- `REVIEW_REQUIRED`: upstream source quality or sufficiency is indeterminate and therefore the episode cannot be assessed as adequate or merely limited.

## Governance

Canonical authority remains `governed_reasoning`. The assessment is frozen, consultative, derivational, contextual, and read-only. It does not establish truth/falsity, assign probability, close reasoning, authorize stopping, invoke capabilities, persist results, create Memory/Learning, modify hypotheses/world model, correct or rerun reasoning, change conclusions, grant authority, or start background work.

## Scope boundary

Foundation v1 adds no `ReasoningContextBundle` wiring and no Reflection runtime integration. Productive consumption requires a separate Go/No-Go after certification.
