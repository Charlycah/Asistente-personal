# RF-H — Velar Semantic Relational Grounding v1

## Scope

This increment extends the existing governed reasoning semantic grounding and
grounding-compilation authority with one bounded relational prerequisite family:

`prerequisite --required_for--> dependent`

together with prerequisite unavailability and dependent capability loss.

## Authority and reuse

- Canonical authority remains `governed_reasoning`.
- Existing contextual rule interpretation is reused unchanged.
- Existing `GovernedBoundedSemanticRoleRelationGrounder` is extended; no parallel
  Velar grounder is introduced.
- Existing `GovernedContextualRuleGroundingCompiler` is extended; no parallel
  compiler is introduced.
- Existing `ContextualRuleRoleBinding` and object-aware `object_role_id`
  instantiation are reused unchanged.

## Bounded family

Family id: `relational_prerequisite_capability_block_v1`.

The v1 family requires exactly two explicit conditions and one conclusion in
already-supported IF/AND/THEN grammar. It grounds exactly two roles:
`prerequisite` and `dependent`.

The compiler emits the relational condition with
`object_role_id="dependent"` rather than encoding `dependent` as a literal
object value.

## Explicit non-goals

This increment does not add historical Velar grammar compatibility, recursive
or multi-hop propagation, persistence, Memory, Learning, world-model mutation,
action execution, provider/retrieval use, or authority gain.

## Fail-closed behavior

Unsupported relation shapes, missing/ambiguous role binding, scope mismatch,
provenance mismatch, and non-canonical semantic slots do not expose a partial
executable rule.

## Validation

Focused architecture/regression suite must remain green. Final certification
requires repository-wide `ruff check .` and `pytest -q`.
