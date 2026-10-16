# Post-M409.1 — Governed Reasoning Method Provenance Foundation v1

## Purpose

Represent, under the existing `governed_reasoning` authority, the explicit structural method of one reasoning episode using only certified lineage already present in governed reasoning artifacts.

## Semantic boundary

`method` means the canonical composition of reasoning operations that are explicitly demonstrated by supplied artifacts. It does not mean optimal strategy, cognitive style, effectiveness, correctness, causal explanation, or a method selected for future execution.

## Inputs

- Required: `GovernedHypothesisDeepeningReport`.
- Optional method evidence: `GovernedMultiHypothesisDiscriminationReport`, `GovernedHypothesisEpistemicDeltaReport`, `GovernedHypothesisUpdateSemanticsReport`.
- Optional assessment lineage: `GovernedEpistemicSufficiencyAssessment`, `GovernedReasoningQualityAssessment`.

The Foundation derives operation kinds; callers cannot declare them manually.

## Method operations v1

1. `HYPOTHESIS_DEEPENING`
2. `MULTI_HYPOTHESIS_DISCRIMINATION`
3. `EPISTEMIC_DELTA`
4. `HYPOTHESIS_UPDATE_SEMANTICS`

Only operations backed by supplied certified artifacts appear. `HYPOTHESIS_DEEPENING` is always required.

## Identity

`method_fingerprint` is structural and depends only on `source_kind` plus canonical operation composition. Different episodes may therefore share one method fingerprint.

`source_fingerprint` and `provenance_id` are episode-specific and include source/snapshot/report lineage plus optional assessment IDs. Sufficiency and Quality never change the method fingerprint.

## Governance

The result is immutable, read-only, derivational and consultative. It does not evaluate effectiveness, rank/select/recommend methods, establish truth or causality, assign probability, modify or rerun reasoning, invoke Curiosity/Reflection, create Learning/Memory, persist results, execute actions, or grant authority.

## Import boundary

The Foundation remains entirely inside `core/governed_reasoning/` and reuses only existing governed reasoning contracts. No producer contract is modified.
