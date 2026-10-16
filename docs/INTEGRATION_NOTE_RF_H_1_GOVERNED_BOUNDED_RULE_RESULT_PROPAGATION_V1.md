# RF-H/1 — Governed Bounded Rule-Result Propagation v1

## Scope

This increment extends the existing `GovernedInferenceEngine` with one bounded
intra-run propagation pass. It does not create a second inference authority,
registry, context model, persistence path, or reasoning subsystem.

## Governed route

The engine now evaluates all eligible rules against the original immutable
`ReasoningContextBundle` first. Eligible base-pass `RULE_RESULT` claims are then
collected into an ephemeral propagation view and only rules that were
`NOT_APPLICABLE` in the base pass may be re-evaluated once against:

`original context claims + eligible base-pass rule-result claims`

Outputs produced during the propagation pass are never re-injected. Therefore
v1 supports A -> B while structurally preventing A -> B -> C in the same run.

## Eligibility and deduplication

Only outputs from base-pass `APPLIED` or `REVIEW_REQUIRED` results are eligible.
They must remain `ClaimType.RULE_RESULT`. Semantically duplicate derived claims
are deduplicated for propagation, and a derived semantic claim already present
in the original context is not re-injected.

## Epistemic preservation

A `REVIEW_REQUIRED` propagated input forces the consuming rule result to remain
`REVIEW_REQUIRED`, even when the target rule itself does not require review.
Propagation therefore cannot strengthen epistemic status.

## Authority and mutation boundaries

- Canonical authority remains `GovernedInferenceEngine` / `governed_reasoning`.
- The original `ReasoningContextBundle` is not mutated.
- The inference rule registry is not mutated by propagation.
- Derived claims are not persisted or written to Memory or Learning.
- No world-model mutation, action execution, provider use, retrieval use, or
  authority gain is introduced.

## Explicit non-goals

This increment does not add recursive chaining, fixed-point inference,
transitive closure, graph reasoning, arbitrary multi-hop propagation, rule
learning, rule synthesis, persistence, Memory, Learning, or action execution.

## Validation

Focused RF-H/1 tests cover Neral -> Velar propagation, one-pass depth,
registry-order independence, scope and validity boundaries, epistemic
preservation, semantic deduplication, and context immutability. Existing Neral,
Velar, case-grounding, admission, and productive-intake regressions are also
validated. Final closure requires repository-wide `ruff check .` and
`pytest -q`.
