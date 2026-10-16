# ROBY XI.2 — Explanatory Model Composition

## Multi-Hypothesis → Explanatory Model → Productive Consultative Consumption

**Entry baseline:** 13,495 PASS + Ruff clean.

## Architectural decision

The post-CAP-08 inventory was reconciled before implementation. CAP-05 already owns
hypothesis deepening, multi-hypothesis discrimination, epistemic gaps and productive
read-only discrimination consumption. The demonstrated residual was not a missing
hypothesis engine: ROBY had no canonical higher-order representation that kept
multiple governed hypotheses together as one explanatory model while preserving
component-local evidence, gaps, pairwise discrimination and exact lineage.

Decision: **existing-owner extension under `governed_reasoning`**. No Theory Engine
and no new cognitive authority.

## Implemented block

New bounded primitive:
`core/governed_reasoning/explanatory_model_composition.py`.

It composes an already-governed `GovernedHypothesisDeepeningReport` and its existing
`GovernedMultiHypothesisDiscriminationReport` into one deterministic
`GovernedExplanatoryModelCandidate`.

The model preserves:

- each hypothesis proposition;
- each hypothesis evidence relation;
- component-local evidence references;
- component-local unresolved epistemic gaps;
- pairwise discrimination relations;
- unresolved discrimination requirement identifiers;
- source report, world snapshot and discrimination lineage.

Fail-closed statuses cover insufficient hypotheses, source review, degraded sources
and lineage mismatch.

## Productive consumption

`app/governed_explanatory_model_productive_consumption.py` reuses the existing
`GovernedMultiHypothesisProductiveConsumptionV1` and then invokes the new composer.
A valid model can expose explicit consultative context. It is not automatically
promoted to truth, causality, Memory, Learning, Structural Transfer or action.

## Governance

The model is read-only and consultative. It does not persist results, create facts,
establish truth or causality, create questions, create Learning, modify Memory or
World Model, execute transfer, execute actions, or grant authority.

## Validation

Seven new architecture tests cover multi-hypothesis composition, component-local
evidence/gaps, fail-closed single-hypothesis behavior, review-required behavior,
reuse of existing productive discrimination, consultative context, and strict
non-authoritative boundaries.

Expanded focused hypothesis perimeter: **22 PASS**.

Official promotion remains gated by local `ruff check .` and full `pytest -q`.
Expected full count if no unrelated test changes exist: **13,502 PASS**.

## Import-boundary correction after full-suite certification attempt

The first full-suite run exposed one historical import-boundary regression: exporting
Explanatory Model Composition eagerly from `core.governed_reasoning.__init__` caused
`cognitive_maturity.epistemic -> governed_reasoning.__init__ ->
explanatory_model_composition -> hypothesis_deepening -> cognitive_maturity.epistemic`.

The correction removes only those eager package-root re-exports. Production and tests
continue to import the bounded primitive from its owning module,
`core.governed_reasoning.explanatory_model_composition`. No cognitive semantics,
authority, productive-consumption behavior, or historical test contract was changed.

Focused corrected perimeter: **23 PASS**, including the historical subprocess import
boundary plus explanatory composition, hypothesis deepening, multi-hypothesis
discrimination and productive consumption controls. `py_compile` passed.

Official promotion remains gated by local `ruff check .` and full `pytest -q`.
