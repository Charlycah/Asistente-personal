# RC-1.4 — Governed Transfer Admission Guard v1

## Purpose

RC-1.4 verifies that one RC-1.3 transfer-instantiation package is eligible for
temporary admission and then delegates registration to the existing canonical
`GovernedTemporaryConcreteRuleAdmissionBoundary`.

RC-1.4 is an eligibility/provenance guard, not a second admission authority.

The bounded flow is:

`RC-1.3 TRANSFER_INSTANTIATED -> RC-1.4 lineage guard -> canonical temporary
admission -> existing registry`

## Canonical authority reuse

- `GovernedTransferAdmissionGuard` never constructs `InferenceRule`.
- It never calls `registry.register()` directly.
- `GovernedTemporaryConcreteRuleAdmissionBoundary` remains the single authority
  that converts an instantiated candidate into a temporary inference rule.
- `GovernedInferenceEngine` is unchanged.

The canonical boundary continues to enforce `temporary=True`,
`requires_review=True`, scope, domains, and validity window.

## Eligibility checks

RC-1.4 requires:

- RC-1.3 status `TRANSFER_INSTANTIATED`;
- exact requested scope;
- a present instantiated candidate;
- complete SHA-256 provenance;
- a valid RC-1.3 package fingerprint recomputed from the package lineage and
  instantiated candidate.

Any failure before canonical admission leaves the registry unchanged.

## Preserved transfer lineage

A successful `GovernedTransferAdmission` preserves:

- RC-1.3 package fingerprint;
- source cognitive-memory id and content fingerprint;
- source grounding fingerprint;
- source compilation fingerprint;
- RC-1 structural-transfer candidate fingerprint;
- RC-1.2 target-projection fingerprint;
- instantiated-candidate fingerprint;
- the canonical temporary-rule admission.

This allows the admitted rule to be traced back through the complete structural
transfer path without changing the canonical inference-rule schema.

## Outcomes

- `ADMITTED_FOR_REVIEW`
- `NOT_TRANSFER_INSTANTIATED`
- `PROVENANCE_MISMATCH`
- `SCOPE_MISMATCH`
- `UNSUPPORTED`

There is no `APPLIED` outcome because RC-1.4 does not perform inference.

## Epistemic behavior

Rules admitted through RC-1.4 remain `requires_review=True`. Existing inference
therefore produces `REVIEW_REQUIRED` and a `RULE_RESULT` whose claim status is
also `REVIEW_REQUIRED` when the transferred rule's conditions are satisfied.

RC-1.4 does not weaken or bypass that status.

## Governed limits

RC-1.4 does not persist transfer metadata, modify Memory or Learning, mutate the
world model, establish truth, execute actions, call providers, perform
retrieval, grant authority, or create a second registry/admission path.

It enables only session-local, time-bounded, scope-bounded reasoning under the
existing review requirement.

Final repository closure requires `ruff check .` and full `pytest -q`.
