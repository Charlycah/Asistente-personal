# ROBY XI.2 — INTEL-G15 — SURGICAL GREEN

## Scope

Close only the G15 RED seam:

`ApprovedKnowledgeRevisionEvidence -> GovernedKnowledgeRevisionApplicationProposal -> existing OfficialMemoryGateway boundary`

No Memory mutation is performed in this gate.

## Production change

Added only:

- `app/governed_knowledge_revision_application_proposal.py`

The new module declares:

- `GovernedKnowledgeRevisionApplicationProposal`
- `GovernedKnowledgeRevisionApplicationProposalFoundation`

The foundation accepts G14 `ApprovedKnowledgeRevisionEvidence` plus explicit `owner`, derives a deterministic source fingerprint, and returns an immutable proposal preserving G13/G14 lineage and the canonical authority string `OfficialMemoryGateway`.

## Frozen boundaries

The proposal is read-only and asserts all execution flags false. The module does not call or instantiate Memory mutation authorities or stores. In particular it contains no calls to `update_content`, `archive`, `remember_governed_learning`, `store_governed_learning`, `OfficialMemoryGateway`, `CognitiveMemoryStore`, or `MemoryRuntimeIntegration`.

`REVISION APPROVED != APPLIED`

`APPLICATION PROPOSED != EXECUTED`

`REPLACEMENT PROPOSED != PERSISTED`

`SUPERSESSION PROPOSED != APPLIED`

`SUPERSEDED != DELETED`

`OLD VERSION MUST REMAIN TRACEABLE`

`ONE MEMORY AUTHORITY`

## Validation performed in construction environment

- G11 through G15 architecture tests: `25 passed`
- M361 quality-baseline tests after regeneration: `5 passed`
- production module compiles
- no lines over 88 characters in the new production module
- forbidden Memory mutation tokens absent from the new module

Full-suite and Ruff certification remain local because Ruff is unavailable in the construction environment and the complete suite exceeded the execution limit.
