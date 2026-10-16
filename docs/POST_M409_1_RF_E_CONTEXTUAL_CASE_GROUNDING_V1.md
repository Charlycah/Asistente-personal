# RF-E — Concrete Case Role Binding / Case Grounding v1

## Status

Implementation v1. Official closure requires `ruff check .` and the complete
`pytest -q` suite on the certified user baseline.

## Purpose

Ground explicit concrete case entities into the abstract roles already certified
by the RF-E Grounding Bridge, without creating entity authority, semantic memory
or a second reasoning path.

The capability remains under the canonical `governed_reasoning` authority and is
bounded to the certified `exclusive_dependency_capability_loss_v1` family.

## Boundary

The case grounder consumes:

1. explicit current-case text;
2. a `ContextualRuleInstantiationSpec` compiled by the certified Grounding Bridge;
3. the same session `scope_reference`; and
4. an explicit case `source_reference`.

It emits `ContextualRuleRoleBinding` values only when all required roles are
explicit and unambiguous: `dependent`, `resource`, and `capability`.

The v1 family additionally requires explicit exclusive dependency, explicit
unavailability of the same resource, and explicit absence of an alternative.
Unknown, ambiguous, contradictory or unsupported cases fail closed and expose no
partial bindings.

## Entity identity and provenance

No entity repository or generated entity identifier is introduced. Binding
identity is the normalized explicit source span from the case text, while the
original source text and source reference remain attached as provenance.

The grounder does not use conversational journal lookup, Memory, World Model,
retrieval, provider/LLM inference, fuzzy matching or implicit coreference.

## 3A.4 handoff

A complete case grounding can be passed directly to the existing
`GovernedContextualRuleInstantiator` together with the abstract spec from the
Grounding Bridge. The v1 tests require this combination to reach
`ContextualRuleInstantiationStatus.INSTANTIATED`.

This capability does not admit the resulting concrete candidate, register a rule
or invoke inference.

## Governed invariants

The result is frozen, read-only and session-local. It adds no persistence, Memory
or Learning write, World Model mutation, truth establishment, inference
authorization, rule registration, action execution, retrieval, provider use,
runtime wiring or authority gain.

## Deferred work

- RF-E/3A.6 admission remains a separate certified boundary.
- RF-E/3A.7 productive consumption remains a separate certified boundary.
- GAP A contextual-rule grammar widening remains out of scope.
- RF-E/3A.8 productive intake remains paused until residual prerequisites are
  re-audited after this capability is certified.
