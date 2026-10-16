# Post-M409.1 — Governed Longitudinal Reasoning Assessment Foundation v1

## Purpose

Add a pure, governed cross-episode assessment over explicitly supplied and comparable
Reasoning Quality + Epistemic Sufficiency results.

## Scope

The Foundation does not retrieve history. The caller supplies the complete series as
neutral `GovernedReasoningAssessmentObservation` values. Live Quality/Sufficiency
objects are admitted through `from_assessments(...)`; future admitted history readers
can supply the same neutral contract without reconstructing full reports. A series is
comparable only when every episode has the same explicit `source_reference`.
`world_snapshot_id` values may differ and are retained only as lineage.

The Foundation derives one of:

- `insufficient_history`
- `consistently_adequate`
- `recurrent_limitation`
- `recurrent_review_required`
- `mixed`

At least two distinct episode assessments are required before recurrence can be
reported. Counts are explicit; no score, probability, confidence percentage, temporal
trend, causal interpretation or strategy recommendation is produced.

## Governance

Canonical authority remains `governed_reasoning`. The result is immutable, read-only,
consultative and derivational. It does not establish truth or correctness, authorize
review/stopping, rerun or change reasoning, invoke Reflection/Learning, persist history,
create Memory/Learning candidates, modify hypotheses/world model, grant authority or
start background work.

`RECURRENT_LIMITATION` means only that `LIMITED` assessments recur in the supplied
comparable series. It is explicitly not a claim that reasoning failed.

## Boundaries

- No `HistoricalAnalysisAuthority` reuse or modification.
- No Cognitive Maturity import dependency.
- No automatic history source.
- No Memory or Learning wiring.
- No ReasoningContextBundle productive consumption in this increment.
- No temporal `improving` / `degrading` semantics.

## Validation target

The increment adds focused architecture tests for recurrence semantics, explicit
insufficient history, mixed history, comparability, lineage, duplicate rejection,
order determinism, immutability and no-power invariants.
