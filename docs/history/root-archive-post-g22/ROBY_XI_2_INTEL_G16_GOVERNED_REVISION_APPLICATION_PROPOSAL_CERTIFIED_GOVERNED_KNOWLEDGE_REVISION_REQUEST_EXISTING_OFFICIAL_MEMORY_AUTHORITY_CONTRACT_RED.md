# ROBY XI.2 — INTEL-G16 — CONTRACT RED

## Gate

**GOVERNED REVISION APPLICATION PROPOSAL → CERTIFIED GOVERNED KNOWLEDGE REVISION REQUEST → EXISTING OFFICIAL MEMORY AUTHORITY**

## Architectural purpose

Expose the real post-G15 seam without performing any Memory mutation.

G16 requires a revision-specific certified request that preserves the complete
G15 lineage, scopes authorization to the exact approved target version, defines
replacement idempotency, and targets the already-existing `OfficialMemoryGateway`.

## Required contract

Expected module:

`app.governed_knowledge_revision_request`

Expected types:

- `GovernedKnowledgeRevisionRequest`
- `GovernedKnowledgeRevisionRequestFoundation`

Expected foundation seam:

`certify(proposal=GovernedKnowledgeRevisionApplicationProposal)`

The request must preserve:

- G15 application proposal identity and fingerprint;
- G14 approval identity and human approval fingerprint;
- G13 revision proposal identity and evidence lineage;
- target owner, memory id, category, and approved current content;
- replacement content;
- an explicit target-state/version fingerprint;
- a deterministic replacement idempotency key.

The request must target the existing authority boundary:

- `writer_authority = "memory_gateway"`
- `writer_component = "OfficialMemoryGateway"`
- `writer_method = "apply_governed_knowledge_revision"`
- `requires_official_memory_gateway = True`
- `requires_atomic_revision = True`
- `preserves_prior_version = True`

## Frozen distinctions

- APPLICATION PROPOSAL != REVISION REQUEST
- REVISION REQUEST != EXECUTION
- APPROVED AGAINST v1 != AUTHORIZED AGAINST A CHANGED TARGET
- REPLACEMENT WRITE != SUPERSESSION
- BOTH MUST FORM ONE LOGICAL REVISION
- SUPERSEDED != DELETED
- OLD VERSION MUST REMAIN TRACEABLE
- ONE MEMORY AUTHORITY

## RED boundary

G16 must not call or instantiate Memory mutation authorities or primitives.

Forbidden in the G16 production module:

- `update_content(`
- `.archive(`
- `store_candidate_idempotent(`
- `remember_governed_learning(`
- `store_governed_learning(`
- `OfficialMemoryGateway(`
- `CognitiveMemoryStore(`
- `MemoryRuntimeIntegration(`

No production implementation belongs in CONTRACT RED.
