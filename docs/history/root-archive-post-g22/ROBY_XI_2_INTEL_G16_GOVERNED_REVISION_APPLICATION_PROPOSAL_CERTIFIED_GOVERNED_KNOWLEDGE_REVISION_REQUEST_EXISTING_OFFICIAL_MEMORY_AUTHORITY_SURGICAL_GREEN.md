# ROBY XI.2 — INTEL-G16 — SURGICAL GREEN

## Gate

**GOVERNED REVISION APPLICATION PROPOSAL → CERTIFIED GOVERNED KNOWLEDGE REVISION REQUEST → EXISTING OFFICIAL MEMORY AUTHORITY**

## Surgical implementation

G16 adds one production module:

`app/governed_knowledge_revision_request.py`

It introduces only:

- `GovernedKnowledgeRevisionRequest`
- `GovernedKnowledgeRevisionRequestFoundation`

The foundation certifies the already-governed G15 application proposal into an
inert revision-specific request. It preserves G13/G14/G15 lineage, binds the
approved target to owner + memory id + category + expected current content,
derives a deterministic target fingerprint, and derives deterministic
replacement idempotency.

The request targets the existing boundary:

- `writer_authority = "memory_gateway"`
- `writer_component = "OfficialMemoryGateway"`
- `writer_method = "apply_governed_knowledge_revision"`
- `requires_official_memory_gateway = True`
- `requires_atomic_revision = True`
- `preserves_prior_version = True`

## Explicit STOP

G16 does not execute the request.

It does not modify `OfficialMemoryGateway`, `MemoryRuntimeIntegration`, or
`CognitiveMemoryStore`, and does not persist a replacement, supersede the old
version, archive Memory, or perform any Memory mutation.

## Frozen distinctions

- APPLICATION PROPOSAL != REVISION REQUEST
- REVISION REQUEST != EXECUTION
- APPROVED AGAINST v1 != AUTHORIZED AGAINST A CHANGED TARGET
- REPLACEMENT WRITE != SUPERSESSION
- BOTH MUST FORM ONE LOGICAL REVISION
- SUPERSEDED != DELETED
- OLD VERSION MUST REMAIN TRACEABLE
- ONE MEMORY AUTHORITY
