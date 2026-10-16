# ROBY XI.2 — CAP-07 Productive Abstraction Episode & Gateway GREEN-5 → GREEN-7

**Baseline entering block:** 13,447 PASS + Ruff clean.

## Implemented

- Existing `ProductiveTemporaryRuleIntake` now exposes the exact semantic grounding it
  already produced; no second semantic grounder was introduced.
- `OfficialGovernedReasoningRuntimeGateway` owns one
  `GovernedProductiveAbstractionAdmission` instance.
- Eligible productive intake evidence is admitted only when productive intake is
  enabled and an exact scope is present.
- Same-turn canonical abstraction episodes are stored transiently by owner/session/turn.
- `CanonicalProductiveReasoningSource` exposes exact abstraction reference IDs and
  consultative context lines.
- `ReasoningRuntimeContributor` consumes those lines read-only.

## Preserved prohibitions

- no Memory write;
- no Learning creation or automatic learning bridge call;
- no Structural Transfer call;
- no inference-rule registration by abstraction;
- no action execution;
- no new authority;
- no arbitrary free-text abstraction path.

## Focused validation

46 PASS:
- 8 GREEN-1→4 tests;
- 5 GREEN-5→7 tests;
- 33 existing CAP-07/CAP-08 perimeter tests.

Full promotion still requires local `ruff check .` and complete `pytest -q`.

## Residual after this block

Productive reachability is closed. The next CAP-07 residual is:

> compose multiple governed relational abstractions into one bounded hierarchical
> concept representation without duplicating semantic grounding, structural transfer,
> Learning, Memory, or epistemic authority.
