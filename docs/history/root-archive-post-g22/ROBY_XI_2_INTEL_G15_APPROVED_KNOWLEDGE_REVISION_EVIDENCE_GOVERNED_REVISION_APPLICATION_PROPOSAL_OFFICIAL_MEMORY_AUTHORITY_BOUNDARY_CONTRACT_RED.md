# ROBY XI.2 — INTEL-G15 — CONTRACT RED

## Gate
APPROVED KNOWLEDGE REVISION EVIDENCE
→ GOVERNED REVISION APPLICATION PROPOSAL
→ EXISTING OFFICIAL MEMORY AUTHORITY BOUNDARY

## Certified source
INTEL-G14 — SURGICAL GREEN, locally certified by the user at:
**14,142 PASS · Ruff clean · 0 FAIL · 0 regressions**.

Before adding G15 RED, this handoff integrates the user-corrected:
- `app/m369_explicit_human_learning_approval.py` import ordering;
- G14 CONTRACT RED test formatting/import correction.

## Architectural decision
G15 does **not** apply a revision. It introduces only the missing inert contract
between already-approved G14 revision evidence and the existing canonical Memory
writer boundary.

`OfficialMemoryGateway` remains the only canonical Memory authority.

G15 MUST NOT create a second Memory gateway, writer, revision store, manager, or
persistence authority.

## Required RED seam
Expected module:
`app.governed_knowledge_revision_application_proposal`

Expected contracts:
- `GovernedKnowledgeRevisionApplicationProposal`
- `GovernedKnowledgeRevisionApplicationProposalFoundation`
- `propose(approved_revision=..., owner=...)`

The proposal must preserve:
- G14 approval identity;
- G13 revision proposal identity/fingerprint;
- target durable Memory identity;
- explicit Memory owner/scope identity;
- current content and replacement content;
- corrective evidence lineage;
- human approval fingerprint;
- canonical Memory authority = `OfficialMemoryGateway`.

## Mandatory boundaries
REVISION APPROVED != APPLIED
APPLICATION PROPOSED != EXECUTED
REPLACEMENT PROPOSED != PERSISTED
SUPERSESSION PROPOSED != APPLIED
SUPERSEDED != DELETED
OLD VERSION MUST REMAIN TRACEABLE
ONE MEMORY AUTHORITY

The G15 proposal is inert:
- no `update_content()`;
- no archive;
- no Memory write;
- no replacement persistence;
- no supersession mutation;
- no `OfficialMemoryGateway` instantiation;
- no `CognitiveMemoryStore` instantiation;
- no `MemoryRuntimeIntegration` instantiation;
- no action/automation;
- no authority expansion.

## Expected RED
Four intentional failures proving the missing application-proposal seam and one
pass proving that the existing `OfficialMemoryGateway` remains unique and the
G14 approval evidence remains the certified source contract.
