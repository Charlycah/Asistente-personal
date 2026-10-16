# ADR-090 — Reflection Engine

## Status

Accepted for M88.

## Context

M49 performs operational reflection inside a cognitive cycle and M87 evaluates one
governed reasoning result. Phase IX still needs a longitudinal faculty that can
compare multiple assessments, identify recurring patterns and produce reviewable
recommendations without changing knowledge, models, decisions or policy.

## Decision

Add `core.adaptive_cognition.reflection_engine` with immutable observations and
reflection records, deterministic trend and recurrence analysis, repository
contracts and optional Cognitive Pipeline integration.

M88 consumes M87 assessments and may reference M85 episodes and M86 mental models.
Those sources remain immutable. Recommendations are advisory inputs for M89 and
cannot promote knowledge or authorize action.

## Consequences

- M49 remains backward-compatible and operational.
- M88 owns longitudinal adaptive reflection.
- All records preserve source assessment identifiers.
- Degrading, mixed or high-importance patterns require review.
- Knowledge evolution remains outside M88.
