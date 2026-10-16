# RF-H — Velar Relational Case Grounding & Productive Admission v1

## Scope

This increment extends the existing governed contextual case-grounding and
case-claim projection route so the already-certified Velar relational family can
reach the canonical temporary-rule admission boundary.

## Authority and reuse

- Canonical authority remains `governed_reasoning`.
- Existing `GovernedContextualCaseRoleGrounder` is extended; no Velar-specific
  parallel grounder is created.
- Existing contextual case claim projection is reused and made object-role aware.
- Existing `ContextualRuleRoleBinding`, instantiator, temporary admission boundary,
  and canonical inference registry remain authoritative.
- Existing ProductiveTemporaryRuleIntake orchestration is unchanged.

## Certified bounded family

`relational_prerequisite_capability_block_v1`

A concrete case must explicitly identify one prerequisite/dependent relation and
explicit prerequisite unavailability. The grounder produces exactly:

- `prerequisite -> concrete prerequisite entity`
- `dependent -> concrete dependent entity`

The relational projected claim resolves `object_role_id="dependent"` through
that same binding rather than treating the role identifier as a literal.

## Productive route

`SPEC_STORED -> case grounding -> claim projection -> instantiation ->
temporary rule admission -> canonical registry`

No second intake, registry, inference engine, or authority is introduced.

## Fail-closed behavior

The route exposes no partial bindings for missing relational roles, multiple
relational candidates, non-distinct roles, unknown prerequisite availability,
explicit prerequisite availability, unsupported rule shapes, or scope mismatch.

## Explicit non-goals

This increment does not add rule-result propagation, recursive chaining,
multi-hop inference, fixed-point evaluation, historical Velar grammar
compatibility, persistence, Memory, Learning, world-model mutation, provider or
retrieval use, action execution, or authority gain.

## Validation

Focused architecture/regression validation covers Velar productive admission and
the existing Neral route. Final closure requires repository-wide `ruff check .`
and `pytest -q`.
