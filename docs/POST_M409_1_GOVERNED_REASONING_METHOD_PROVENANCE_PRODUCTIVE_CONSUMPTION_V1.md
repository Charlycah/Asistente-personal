# Post-M409.1 — Governed Reasoning Method Provenance — ReasoningContextBundle Productive Consumption v1

## Purpose

Expose a certified `GovernedReasoningMethodProvenance` through the existing
`ReasoningContextBundle.derived_assessments` structural contract without changing the
Method Provenance Foundation, the context core, M203, Memory, Learning, Reflection,
Curiosity, Planning, or Adaptive Reasoning.

## Productive boundary

The app-level consumer projects one method-provenance artifact into a neutral context
item. Context identity is episode/provenance-specific. `method_fingerprint` remains a
structural method identity and is never used as the bundle item identity, so different
episodes using the same method can coexist.

The projection contains only certified source lineage, operation kinds, and fingerprints.
It does not reconstruct or embed Deepening, Discrimination, Epistemic Delta, Update
Semantics, Sufficiency, or Reasoning Quality reports.

## Reuse

- Reuses the existing `ReasoningContextDerivedAssessment` structural contract.
- Reuses the existing `ReasoningContextBundle.derived_assessments` collection.
- Adds no specialized import to `core/governed_reasoning/context.py`.
- Adds no new context field, registry, authority, or store.

## Governed limits

Productive consumption only makes method provenance available to later governed
reasoning. It does not evaluate method effectiveness, rank/select/recommend methods,
establish causality or truth, assign probability, modify or rerun reasoning, invoke
Curiosity/Reflection, create Learning/Memory, execute actions, persist results, or start
background work.

## Validation target

The increment adds 11 focused architecture tests covering projection, structural-vs-
episode identity, deterministic serialization, idempotence, collision fail-closed,
coexistence with existing derived items, deterministic ordering, no-power surfaces, import
boundaries, and immutability of the source Foundation/context input.
