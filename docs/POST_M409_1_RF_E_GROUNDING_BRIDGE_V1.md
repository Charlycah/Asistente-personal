# RF-E — Grounding Bridge v1

## Status

CLOSED/PASS on the certified user baseline: 12,155 tests passed and Ruff clean.

## Purpose

Compile an already certified bounded semantic grounding into the existing
contextual-rule contracts without adding semantic authority or concrete case
bindings.

The bridge remains under the canonical `governed_reasoning` authority and reuses:

1. Bounded Semantic Role/Relation Grounding v1.
2. RF-E/3B.5B temporary contextual predicate vocabulary.
3. RF-E/3B.5C governed contextual claim normalization.
4. RF-E/3A.4 contextual rule instantiation specification contracts.

## Boundary

The bridge accepts only a provenance-matched, session-scoped contextual rule
candidate plus a `GROUNDED` semantic-grounding candidate from the certified
`exclusive_dependency_capability_loss_v1` family.

It deterministically produces a temporary vocabulary, normalized abstract claims
and a `ContextualRuleInstantiationSpec`. It does **not** produce concrete
`ContextualRuleRoleBinding` objects.

Consequently 3A.4 still fails closed with `INSUFFICIENT_BINDINGS` until a later,
separately governed case-grounding capability supplies explicit entity bindings.

## Governed invariants

The bridge is read-only and session-local. It adds no persistence, Memory or
Learning write, World Model mutation, provider/LLM use, retrieval, rule
registration, inference authorization, action execution, runtime wiring or new
authority.

Non-compiled outcomes expose no partial vocabulary, normalized claims or
instantiation specification.

## Deferred work

- GAP A: widening the contextual-rule grammar remains out of scope.
- Concrete case role binding is implemented separately by RF-E Contextual Case
  Grounding v1 and remains outside the bridge itself.
- RF-E/3A.8 productive intake remains paused until its remaining prerequisites are
  independently audited and certified.
