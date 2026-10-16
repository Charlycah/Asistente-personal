# Post-M409.1 — Governed Reasoning Method ↔ Epistemic Outcome Association Foundation v1

## Purpose

Describe, under the existing `governed_reasoning` authority, repeated epistemic outcomes observed across explicitly comparable reasoning episodes that share one certified reasoning method.

## Semantic boundary

An association is observational only. It means that a supplied collection of certified episodes sharing the same `method_fingerprint` and `source_reference` exhibits a categorical recurrence of Reasoning Quality + Epistemic Sufficiency outcomes. It does not mean that the method caused, improved, degraded, succeeded, or failed the reasoning.

## Input observation

`GovernedReasoningMethodOutcomeObservation.from_artifacts(...)` accepts exactly:

- `GovernedReasoningMethodProvenance`;
- `GovernedReasoningQualityAssessment`;
- `GovernedEpistemicSufficiencyAssessment`.

The observation is admitted only when Method Provenance explicitly references that exact Quality and Sufficiency pair and all source, snapshot, Deepening, optional Discrimination, and optional Update Semantics lineage matches fail-closed.

## Comparability v1

Every observation supplied to one association must share:

- the same `method_fingerprint`;
- the same explicit `source_reference`.

Cross-source association and comparison between different methods are intentionally excluded from v1. World snapshots may differ between episodes, while each individual observation must preserve exact within-episode snapshot lineage.

## Statuses

- `INSUFFICIENT_EVIDENCE`: fewer than two admitted observations;
- `CONSISTENTLY_ADEQUATE`: every observation is `ADEQUATE` + `SUFFICIENT`;
- `RECURRENT_LIMITATION`: every observation is `LIMITED` + `INSUFFICIENT`;
- `RECURRENT_REVIEW_REQUIRED`: every observation is `REVIEW_REQUIRED` + `INDETERMINATE`;
- `MIXED`: every other combination.

No majority or predominance rule exists in v1.

## Identity and counts

Association identity is deterministic and independent of caller ordering. It is derived from schema version, `method_fingerprint`, `source_reference`, and canonical observation identities. The result exposes categorical counts only; no rate, score, probability, confidence, or effectiveness metric is created.

## Governance

The Foundation is immutable, read-only, derivational and consultative. It does not establish truth/falsity/causality, evaluate effectiveness, compare/rank/select/recommend methods, modify or rerun reasoning, change reasoning method, invoke Adaptive Reasoning/Curiosity/Reflection, create Learning/Memory, persist results, execute actions, grant authority, or start background processes.

## Import boundary

The Foundation lives in `core/governed_reasoning/` and composes only existing certified governed reasoning artifacts. It does not modify Method Provenance, Quality, Sufficiency, Longitudinal Reasoning, `ReasoningContextBundle`, M203, Learning, or Memory contracts.
