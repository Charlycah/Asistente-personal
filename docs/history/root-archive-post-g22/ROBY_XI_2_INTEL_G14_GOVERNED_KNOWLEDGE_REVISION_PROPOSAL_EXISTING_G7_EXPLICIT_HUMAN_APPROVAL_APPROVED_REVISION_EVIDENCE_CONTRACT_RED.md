# ROBY XI.2 — INTEL-G14 — CONTRACT RED

## Gate
GOVERNED KNOWLEDGE REVISION PROPOSAL
→ EXISTING G7 EXPLICIT HUMAN APPROVAL AUTHORITY
→ APPROVED REVISION EVIDENCE

## Certified source
INTEL-G13 — SURGICAL GREEN — locally certified:
14,137 PASS · Ruff clean · 0 FAIL · 0 regressions.

The user-corrected G13 production file and corrected G13 RED test are integrated
into this handoff before the G14 RED additions.

## Architectural decision
G14 MUST reuse `M369ExplicitHumanLearningApprovalEvidenceFoundation` as the
existing explicit-human-approval authority.

G14 MUST NOT create a second approval authority, manager, gateway, or writer.

The existing learning-specific DTOs are not source-neutral enough for revision
approval because they require learning/preference/evaluation identifiers.
G14 therefore requires revision-specific evidence contracts under the SAME G7
approval authority.

## Required RED seam
The existing G7 foundation must expose a bounded revision approval seam such as
`evaluate_revision(proposal, response)`.

The revision approval response must link exactly to the G13 proposal identity
without fabricated:
- `learning_candidate_id`;
- `preference_candidate_id`;
- `evaluation_report_id`.

Approved revision evidence must preserve:
- approval identity;
- revision proposal identity;
- target durable Memory identity/category;
- current and proposed content;
- corrective evidence ids;
- G13 proposal fingerprint;
- human response reference;
- approver;
- human approval fingerprint.

## Mandatory boundaries
REVISION PROPOSED != APPROVED
REVISION APPROVED != APPLIED
APPROVED REVISION != MEMORY WRITE
SUPERSEDED != DELETED
HUMAN APPROVAL != EPISTEMIC TRUTH

Approved revision evidence remains inert:
- no Memory write;
- no `update_content`;
- no archive;
- no supersession/retraction;
- no replacement persistence;
- no actions/automation;
- no authority expansion.

## Expected RED
Four intentional failures proving the missing revision-specific seam/contracts,
plus one pass proving the existing G7 authority remains the sole approval
foundation and retains its explicit response vocabulary.
