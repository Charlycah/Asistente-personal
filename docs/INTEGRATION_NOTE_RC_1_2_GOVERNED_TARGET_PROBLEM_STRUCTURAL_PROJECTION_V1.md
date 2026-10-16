# RC-1.2 — Governed Target Problem Structural Projection v1

## Purpose

RC-1.2 converts one ordinary bounded problem statement into a read-only
structural representation of its explicit antecedent premises. It deliberately
does not project or assume the rule conclusion.

The bounded flow is:

`ordinary target problem -> governed case grounding -> target structural
projection -> RC-1 antecedent match -> TRANSFER_CANDIDATE -> STOP`

## Authority and reuse

- `GovernedContextualCaseRoleGrounder` remains the concrete case-role authority.
- RC-1.2 reuses that authority through a non-registerable structural shape spec;
  it does not duplicate dependency or availability parsing.
- `GovernedStructuralKnowledgeTransferMatcher` remains the structural
  compatibility authority.
- No rule is admitted and no inference is authorized by RC-1.2.

## Target structure

For the certified dependency-loss family, a projected target contains exactly:

- dependent role binding;
- resource role binding;
- capability role binding;
- explicit exclusive dependency premise;
- explicit resource-unavailable premise;
- explicit no-alternative premise.

The capability-loss conclusion is not included in `observed_slots`, even when
conclusion-like words happen to appear elsewhere in the target text.

## Antecedent transfer matching

RC-1 can compare a source rule's antecedent signature with a projected target
problem. For v1 this comparison is restricted to
`exclusive_dependency_capability_loss_v1`.

A target therefore does not need to contain the conclusion it is intended to
support. One compatible source produces `TRANSFER_CANDIDATE`; multiple
compatible sources remain `AMBIGUOUS`; unsupported or incomplete targets do not
transfer.

## Fail-closed behavior

Projection exposes no partial structure when:

- exclusivity is not explicit;
- resource availability is unknown;
- alternative status is unknown;
- a positive alternative is explicit;
- multiple dependency candidates are present;
- scope is incompatible.

## Governed limits

RC-1.2 is read-only and session-local. It does not persist results, create or
modify Memory, create or modify Learning, mutate the world model, establish
truth, authorize inference, register rules, execute actions, call providers,
perform retrieval, or grant authority.

## Explicit non-goals

RC-1.2 does not instantiate a recalled rule on the target, admit a transfer,
run inference, learn a generalized rule, perform recursive analogy, or broaden
the certified semantic families.

Final repository closure requires `ruff check .` and full `pytest -q`.
