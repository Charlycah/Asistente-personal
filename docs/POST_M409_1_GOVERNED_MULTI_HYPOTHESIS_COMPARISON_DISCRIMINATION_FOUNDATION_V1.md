# Post-M409.1 — Governed Multi-Hypothesis Comparison / Discrimination Foundation v1

## Status

IMPLEMENTED — pending official project validation gates (`ruff check .` and full `pytest -q`).

## Purpose

Deepen governed reasoning by comparing multiple hypotheses already assessed inside one `GovernedHypothesisDeepeningReport`. The capability identifies evidence shared by a pair, evidence unique to either hypothesis and differences in existing epistemic relations without promoting either hypothesis to fact.

## Canonical authority

`governed_reasoning` remains the sole authority. `GovernedMultiHypothesisDiscriminator` is subordinate, read-only and consultative and has no independent authority identifier.

## Inputs

Foundation v1 consumes exactly one `GovernedHypothesisDeepeningReport`. It does not query M391.3/M391.4 again and does not read world model, memory, sensors, conversation, Curiosity or external sources.

## Outputs

`HypothesisPairComparison` classifies a pair as:

- `INDISTINGUISHABLE`: current explicit evidence and relation do not discriminate the pair.
- `PARTIALLY_DISCRIMINATED`: explicit differential evidence and/or different existing epistemic relations make a qualitative distinction visible.

`DiscriminatingEvidenceRequirement` is emitted only for indistinguishable pairs. It preserves source and world-snapshot lineage and describes missing evidence using existing epistemic gaps when available, otherwise a bounded generic discrimination requirement.

## Semantic boundaries

- more evidence != truth
- compatible != proven
- contradicted != automatically false
- shared evidence != discriminating evidence
- missing evidence != negative evidence
- indistinguishable != equivalent
- discrimination requirement != acquisition plan
- acquisition plan != execution

## Fail-closed behavior

A single hypothesis returns `INSUFFICIENT_HYPOTHESES`. A degraded deepening source returns `DEGRADED`. A source requiring review returns `SOURCE_REVIEW_REQUIRED`. These states generate no fabricated pair comparison or discrimination requirement.

## Explicitly out of scope

Evidence Acquisition Planning, Curiosity wiring for discrimination requirements, conversation emission, persistence, learning, memory writes, action execution, greater independence, M410, networking and Residential.
