# ADR-082 — Governed Inference

## Status

Accepted for M80.

## Context

M77 normalizes evidence, M78 represents claims and M79 assembles a governed reasoning context. ROBY now needs a deterministic way to derive bounded conclusions without treating free-form model output as authority or allowing inferred statements to become facts silently.

## Decision

Introduce a declarative governed inference subsystem in `core.governed_reasoning.inference`.

Each inference rule is immutable and declares:

- stable rule identifier;
- explicit version;
- human-readable description;
- typed claim conditions;
- allowed Scope Guard domains;
- fixed conclusion shape;
- base confidence ceiling;
- review requirement and enabled state.

The initial engine supports equality, membership and temporal comparisons against the query `as_of` instant. Rules operate only on the `ReasoningContextBundle` produced by M79. They never query M72–M78 repositories directly.

Every successful inference produces a new `ClaimType.RULE_RESULT` with `ClaimOrigin.RULE`, an explicit `rule_reference` and deterministic identity. The output remains proposed or review-required and is never promoted to a fact automatically.

The engine is single-pass. Recursive inference, learned rules, probabilistic rule discovery, conflict resolution and external actions remain out of scope.

## Consequences

### Positive

- Deterministic and reproducible inference runs.
- Public rule identity and version traceability.
- Strict separation between evidence-backed claims and derived claims.
- Confidence is bounded by both the rule and its inputs.
- Scope and review constraints remain visible in every result.

### Trade-offs

- The declarative rule language is intentionally limited.
- Rules must be registered explicitly.
- Cross-rule chaining is deferred to a future governed design.
- M81 remains responsible for conflicts and multifactor uncertainty.
