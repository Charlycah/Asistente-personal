# ROBY XI.2 — INTEL-G13 — SURGICAL GREEN

## Scope
Existing durable `STABLE_KNOWLEDGE` plus governed corrective evidence can now
produce an inert `GovernedKnowledgeRevisionProposal`.

## Production change
Added only `app/governed_knowledge_revision_proposal.py`.

The foundation reuses:
- `CognitiveMemoryRecord` as the existing durable Memory record;
- `LearningCategory.STABLE_KNOWLEDGE`;
- governed Reasoning `EvidenceReference` for corrective-evidence identity.

No Memory reader/store/runtime/gateway or Reasoning authority is duplicated.

## Boundary
The proposal preserves target memory identity/category/current content, proposed
replacement content, corrective evidence ids, and a deterministic SHA-256
fingerprint.

It is read-only and review-required.

## Explicitly not authorized
- approval;
- application;
- Memory write/update/archive;
- supersession/retraction;
- replacement persistence;
- actions/automation;
- authority expansion.

CONTRADICTED != WRONG
REVISION PROPOSED != APPROVED
APPROVED REVISION != APPLIED
SUPERSEDED != DELETED

## Selected validation
G13 + G12 + G11: 15 PASS.
Production module compiles.
M361 quality baseline regenerated.

Full Ruff/full pytest certification remains local.
