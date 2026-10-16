# Post-M409.1 — ReasoningContextBundle Derived Assessment Contract Generalization v1

## Purpose
Generalize only the structural typing boundary used by `ReasoningContextBundle.derived_assessments` so multiple already-governed, read-only derived assessment kinds can reuse the existing context surface without teaching the bundle about each capability.

## Contract
`ReasoningContextDerivedAssessment` is a minimal structural `Protocol` exposing only `assessment_id` and `to_dict()`. It is not an authority, registry, manager, persistence surface, reasoning controller, or execution capability.

## Compatibility
- Existing `GovernedDerivedEpistemicAssessment` remains unchanged and conforms structurally.
- Empty historical bundles preserve identity and serialized shape.
- Existing deterministic ordering, duplicate-id rejection, fingerprint participation, and serialization remain unchanged.
- `context.py` no longer imports the hypothesis-update-specific derived assessment type.
- No Sufficiency productive wiring is introduced in this increment.

## Boundaries
No new authority, no Memory/Learning, no Planning, no execution, no reasoning invocation, no new bundle, and no runtime orchestration.
