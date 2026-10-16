# ROBY XI.2 — Higher Cognitive Evolution
## Governed Explicit Hypothesis Source Adapter + Selective Scenario/Causal Reachability Wave

**Baseline de entrada:** 13.413 tests PASS + Ruff limpio.
**Estado:** CLOSED / PROMOTED — full local promotion gate satisfied at **13.439 PASS + Ruff limpio**.

## Purpose

Make the existing scenario/causal governed reasoning foundations reachable only from explicit,
structured, already-certified semantics.

This wave deliberately does not introduce free-text hypothesis extraction.

## New governed source contract

`GovernedExplicitHypothesisSource` is a read-only, derivational value under the existing
`governed_reasoning` authority.

It can explicitly declare one of:

- `NONE`;
- `SCENARIO`;
- `CAUSAL`.

For scenario eligibility, every required field must already exist:

- proposition;
- world domain;
- fact key;
- assumed value;
- temporal scope.

For causal eligibility, every required field must already exist:

- proposition;
- cause domain/key/value;
- effect domain/key/value;
- temporal scope.

Missing semantics are never inferred from prose.

## Applicability states

`GovernedExplicitHypothesisSourceResult` reports:

- `NOT_APPLICABLE`;
- `SCENARIO_ELIGIBLE`;
- `CAUSAL_ELIGIBLE`;
- `REVIEW_REQUIRED`.

Only eligible states contain a hypothesis and a canonical scenario/causal report.

## Existing foundations reused

Scenario-eligible sources are projected to:

`ScenarioHypothesis`
→ existing `GovernedScenarioSimulator`
→ `GovernedScenarioSimulationReport`.

Causal-eligible sources are projected to:

`CausalHypothesis`
→ existing `GovernedCausalPredictiveReasoner`
→ `GovernedCausalPredictionReport`.

No new simulator, prediction engine, world model or reasoning authority was introduced.

## World authority

The adapter requires an existing `PersistentWorldSnapshot`.

It does not build, persist, mutate or replace the world model.

The resulting lineage binds the source fingerprint and exact `world_snapshot_id`.

## Decision-option boundary

Generic `GovernedDecisionOption` values are explicitly insufficient to create hypotheses.

`from_decision_options(...)` returns `NOT_APPLICABLE` because option identity/title alone does not
contain the required world-state or causal semantics.

This prevents:

`Comprar A`
from becoming an invented scenario or causal relation.

## Productive reachability

`OfficialGovernedReasoningRuntimeGateway.evaluate_explicit_hypothesis_source(...)` exposes the
adapter through the same official reasoning authority.

The existing `CanonicalDecisionFacade` can consume the resulting scenario/causal reports without
any new decision authority.

## Governance boundaries

The source/result:

- are read-only;
- are derivational;
- use no LLM;
- use no retrieval;
- persist nothing;
- create no Memory;
- create no Learning;
- do not modify the world model;
- execute no actions;
- grant no authority.

## Validation

Initial RED: module absent.

New wave tests: **11 PASS**.

The tests prove:

- complete scenario semantics become a real scenario report;
- complete causal semantics become a real causal report;
- incomplete semantics fail closed;
- proposition text is never mined for missing fields;
- generic decision options remain NOT_APPLICABLE;
- the official reasoning gateway exposes the same adapter;
- world-snapshot lineage changes when the world changes;
- source lineage requires SHA-256;
- existing Canonical Decision can consume the reached scenario report.

Full local promotion gate satisfied at **13.439 PASS + Ruff limpio**.

## Next causal boundary

This wave makes hypothesis-bearing reasoning selectively reachable.

It does not yet say that every ordinary canonical reasoning turn contains such a source.

The next gate should now revisit:

`Scenario/Causal Report`
→ `Hypothesis Deepening`
→ `Sufficiency`
→ `Quality`
→ `Method Provenance`
→ `Method Outcome`
→ `Strategy Outcome`

only for exact same-turn/source-eligible episodes.
