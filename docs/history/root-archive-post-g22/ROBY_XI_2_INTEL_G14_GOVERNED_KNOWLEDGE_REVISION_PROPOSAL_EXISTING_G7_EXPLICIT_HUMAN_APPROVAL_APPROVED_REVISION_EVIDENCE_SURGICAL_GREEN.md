# ROBY XI.2 — INTEL-G14 — SURGICAL GREEN

## Scope
G13 governed knowledge revision proposal → existing G7 explicit human approval authority → inert approved revision evidence.

## Surgical production change
Only `app/m369_explicit_human_learning_approval.py` is extended.
The existing `M369ExplicitHumanLearningApprovalEvidenceFoundation` remains the sole explicit-human-approval authority.

Added revision-specific DTOs under that same authority:
- `ExplicitHumanKnowledgeRevisionApprovalResponse`
- `ApprovedKnowledgeRevisionEvidence`

Added `evaluate_revision(proposal, response)` to the existing G7 foundation.
No fabricated learning/preference/evaluation identifiers are used.

## Boundaries
The approved revision evidence is read-only and does not write Memory, modify knowledge, apply the revision, archive/supersede Memory, persist a replacement, execute actions, or grant authority.

REVISION PROPOSED != APPROVED
REVISION APPROVED != APPLIED
APPROVED REVISION != MEMORY WRITE
SUPERSEDED != DELETED
HUMAN APPROVAL != EPISTEMIC TRUTH

## Selected validation
G14 + G13 + G12 + G11: 20 PASS.
M361 baseline regenerated.
Full Ruff/full pytest certification remains local.
