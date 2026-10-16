# Post-M409.1 — Governed Comparative Reasoning Method Awareness Foundation v1

## Purpose

Add a narrow, read-only descriptive awareness of whether two already-certified reasoning
methods exhibit the same or different categorical epistemic outcome patterns. The capability
fills the cross-method awareness gap without creating a second authority for Method Provenance
or Method ↔ Epistemic Outcome Association.

## Reused authority and inputs

`governed_reasoning` remains the canonical authority. The Foundation consumes exactly two
existing `GovernedReasoningMethodOutcomeAssociation` artifacts. It does not rebuild method
identity, Reasoning Quality, Epistemic Sufficiency, per-episode observations, or longitudinal
method/outcome associations.

Admission is fail-closed. Both associations must preserve the existing governed authority,
read-only/derivational/consultative contract, have distinct association IDs and distinct
`method_fingerprint` values, and share the same explicit `source_reference`.

## Comparability boundary

In v1, `comparable` means only that two certified association artifacts satisfy the narrow
admission contract for descriptive cross-method inspection. It does not mean experimental
equivalence and does not isolate method choice as a causal variable.

Different observation counts and different `world_snapshot_ids` are admitted and preserved as
lineage. They are not normalized into scores, rates, probabilities, or effectiveness metrics.
Cross-source comparison is rejected rather than classified.

## Derived states

- `INSUFFICIENT_COMPARATIVE_EVIDENCE`: at least one source association is itself
  `INSUFFICIENT_EVIDENCE`; no cross-method difference is inferred.
- `SAME_PATTERN`: both admitted associations have the same existing categorical outcome status.
  This is not a claim that the methods are equivalent.
- `DIFFERENT_PATTERN`: the admitted associations have different existing categorical outcome
  statuses. This is not a causal, effectiveness, failure, or superiority claim.

The Foundation compares only the already-certified categorical association status. It does not
invent majority inference or derive hidden metrics from raw counts.

## Explicit non-authorities

The capability does not establish truth/falsity, causality, probability, effectiveness, method
superiority, ranking, selection, recommendation, adaptation, rerun, Learning, Memory,
persistence, Planning, execution, authority transfer, or background processing.

`compares_methods=True` records the capability's narrow descriptive purpose; all evaluative and
interventional authority flags remain false and are enforced fail-closed by the artifact.

## Scope boundary

Foundation v1 introduces no `ReasoningContextBundle` consumption, app adapter, M203 event schema,
historical store, runtime wiring, or productive consumer. Any productive exposure requires a
separate reuse/admission checkpoint after this Foundation is certified.
