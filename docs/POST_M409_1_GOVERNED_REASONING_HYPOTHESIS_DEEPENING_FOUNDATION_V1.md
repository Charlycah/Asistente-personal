# Post-M409.1 — Governed Reasoning / Hypothesis Deepening Foundation v1

## Status

IMPLEMENTED — validation of the new targeted tests completed. Full project certification remains a user baseline gate.

## Purpose

Deepen already-governed hypotheses without introducing a new reasoning authority and without re-reading source systems. Foundation v1 composes the explicit outputs of M391.3 scenario simulation and M391.4 causal/predictive reasoning.

## Productive contract

`GovernedHypothesisDeepener` accepts either an explicit `GovernedScenarioSimulationReport` or an explicit `GovernedCausalPredictionReport` and returns `GovernedHypothesisDeepeningReport`.

The report preserves:

- canonical authority: `governed_reasoning`;
- source report identity and world-snapshot identity;
- hypothesis identity and proposition;
- explicit fact/evidence references already present in the source report;
- rationale and risk codes;
- hypothesis epistemic level.

Each hypothesis is classified only as:

- `COMPATIBLE`;
- `CONTRADICTED`;
- `UNRESOLVED`.

These labels are evidence relations, not truth promotion.

## Epistemic gap

Only unresolved hypotheses produce `HypothesisEpistemicGap`. A gap contains explicit source lineage, known evidence references, evidence codes, the unresolved hypothesis and a bounded description of what evidence is missing.

The gap is deliberately inert. It has no question-delivery authority and does not import or call Curiosity. A later explicit wiring increment may adapt this structured evidence to the existing Governed Epistemic Curiosity contract.

## Safety / governance invariants

- hypothesis != fact;
- compatibility != proof;
- contradiction != automatic falsification;
- missing evidence != negative evidence;
- association != causality;
- prediction != certainty;
- epistemic gap != question;
- reasoning result != learning;
- learning != persistence without the certified approval chain.

Foundation v1 is read-only and consultative. It cannot persist results, create facts, create questions, create learning candidates, modify world state, memory, learning or planning, execute actions, grant authority or start background processes.

There is no path from Hypothesis Deepening to `OfficialMemoryGateway`.

## Reuse

Foundation v1 reuses M391.3 and M391.4 reports exactly as upstream evidence-bearing contracts. It does not duplicate scenario simulation, causal reasoning, world-model access, Curiosity, Learning or Memory authority.

## Validation performed in implementation environment

- targeted pytest: `3 passed`;
- Python import/compile path exercised through pytest;
- Ruff executable was not available in the implementation container, so project-level Ruff certification remains part of the user's official validation gate.

## Scope exclusions

No M410. No networking. No Residential. No new runtime wiring. No new persistence path. No Curiosity productive wiring in this increment.
