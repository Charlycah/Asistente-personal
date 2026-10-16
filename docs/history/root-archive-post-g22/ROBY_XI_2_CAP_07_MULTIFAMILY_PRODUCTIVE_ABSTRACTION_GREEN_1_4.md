# ROBY XI.2 — CAP-07 Multi-Family Productive Abstraction Normalization GREEN-1 → GREEN-4

**Entry baseline:** 13,468 PASS + Ruff clean.

## Implemented

- explicit `normalization_family_id` on productive abstraction evidence;
- preservation of historical R1 behavior;
- second bounded normalization family R2;
- family-isolated transient accumulation;
- one global item bound per session/scope across all families;
- repeated R2 induction through the existing `GovernedRelationalAbstractionInducer`;
- duplicate evidence remains idempotent.

## Compatibility correction discovered during GREEN

The original RED proposal assigned the exclusive-dependency grounding family to R2.
The historical CAP-07 GREEN-1→4 tests showed that this family is already a protected
R1 contract.

The implementation therefore preserves:

### R1 — historical contract

Grounding family:
`exclusive_dependency_capability_loss_v1`

Normalization:
`required_for`
→ `blocked_when_unavailable`

### R2 — new bounded family

Grounding family:
`relational_prerequisite_capability_block_v1`

Normalization:
`required_for`
→ `blocked_when_prerequisite_unavailable`

R2 is distinct by outcome semantics and exact grounding family. It does not assert
unrestricted causality.

## Governance

Unchanged:

- authority remains `governed_reasoning`;
- no new semantic grounder;
- no new abstraction inducer;
- no Memory;
- no Learning extension;
- no Structural Transfer;
- no World Model or Personal Knowledge mutation;
- no persistence.

## Focused validation

9 new multi-family tests PASS.

Expanded affected perimeter:
**82 PASS**.

Full promotion still requires:

`ruff check .`
`pytest -q`

Expected complete suite if no regressions:
**13,477 PASS + Ruff clean.**
