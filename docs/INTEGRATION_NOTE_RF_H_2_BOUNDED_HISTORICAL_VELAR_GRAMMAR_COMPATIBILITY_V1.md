# RF-H/2 — Bounded Historical Velar Grammar Compatibility v1

## Scope

This increment admits the historical Velar teaching wording into the existing
governed temporary-rule pipeline without creating a parser, semantic family,
compiler, intake, registry, or inference authority.

Historical form:

`si una capacidad X es requisito indispensable para una capacidad Y, la pérdida
de X impide Y mientras siga faltando X`

## Authority and reuse

- `GovernedContextualRuleInterpretationProducer` remains the interpretation
  authority.
- `GovernedBoundedSemanticRoleRelationGrounder` remains the semantic grounding
  authority.
- The existing `relational_prerequisite_capability_block_v1` family is reused.
- The existing grounding compiler emits the already-certified
  `object_role_id="dependent"` contract.
- Productive temporary intake is unchanged.

## Compatibility behavior

The interpreter recognizes the historical two-condition relational shape and
preserves its exact source span. A nested `Principio Velar:` label after
`Regla adicional artificial:` is treated only as an explicit teaching label.

The semantic grounder accepts the bounded historical loss/conclusion surface
form only when the symbolic references are internally consistent with the
explicit prerequisite/dependent declaration. Source-backed slot spans remain
real substrings of the teaching text.

## Fail-closed limits

- prerequisite loss and continuing-missing references must agree;
- conclusion dependent reference must agree with the declared dependent role;
- mixed historical/canonical clause shapes are rejected;
- no partial role mentions or semantic slots are exposed on ambiguity.

## Explicit non-goals

This increment does not change case grounding, multi-pending intake,
rule-result propagation depth, persistence, Memory, Learning, world-model
mutation, actions, provider/retrieval use, or authority.

## Validation

Focused regression validation must include historical and bounded Velar,
RF-H/1 propagation, Velar productive admission, and historical Neral grammar
compatibility. Final certification requires repository-wide `ruff check .` and
`pytest -q`.
