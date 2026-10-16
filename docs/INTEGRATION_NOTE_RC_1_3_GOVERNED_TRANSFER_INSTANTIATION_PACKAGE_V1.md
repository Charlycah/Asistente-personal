# RC-1.3 — Governed Transfer Instantiation Package v1

## Purpose

RC-1.3 converts one certified structural transfer into an instantiated contextual
rule candidate while stopping before temporary-rule admission.

The bounded flow is:

`recall -> RC-1.1 -> RC-1.2 -> RC-1 structural match -> RC-1.3 instantiation -> STOP`

## Source rule preservation

RC-1.1 now retains the complete
`GovernedContextualRuleGroundingCompilation` produced by the existing compiler.
The compilation remains ephemeral and read-only. RC-1.3 does not reconstruct
conditions, predicates, or conclusions from the transfer correspondence.

The source `ContextualRuleInstantiationSpec` is reused exactly.

## Target binding preservation

RC-1.2 remains the authority for target-problem role bindings. RC-1.3 converts
those existing bindings into `ContextualRuleRoleBinding` values carrying the
target source reference and source text.

No target conclusion is projected or assumed.

## Canonical instantiation reuse

`GovernedContextualRuleInstantiator` remains the only authority that resolves
the source rule specification against concrete target bindings.

A successful RC-1.3 result contains:

- source memory id and content fingerprint;
- source grounding fingerprint;
- source compilation fingerprint;
- structural-transfer candidate fingerprint;
- target-projection fingerprint;
- concrete target bindings;
- the existing instantiator's `INSTANTIATED` candidate.

## Lineage checks

RC-1.3 fails closed unless:

- source grounding and source compilation share certified lineage;
- the transfer candidate references exactly that source grounding;
- the transfer candidate references exactly the supplied target projection;
- source, transfer, target, and compilation share the same scope;
- transfer role correspondences agree with both source role mentions and target
  role bindings.

No executable candidate is exposed after a lineage failure.

## Outcomes

- `TRANSFER_INSTANTIATED`
- `NO_TRANSFER`
- `AMBIGUOUS`
- `PROVENANCE_MISMATCH`
- `SCOPE_MISMATCH`
- `UNSUPPORTED`

## Governed limits

RC-1.3 is read-only and session-local. It does not persist results, modify
Memory or Learning, mutate the world model, establish truth, authorize
inference, register rules, execute actions, call providers, perform retrieval,
or grant authority.

The existing temporary-rule admission boundary is deliberately not called.

## Explicit non-goals

RC-1.3 does not admit the transferred rule, run inference, persist transfer
results, select among ambiguous source structures, alter the source rule
semantics, synthesize a new rule, or authorize autonomous application.

Final repository closure requires `ruff check .` and full `pytest -q`.
