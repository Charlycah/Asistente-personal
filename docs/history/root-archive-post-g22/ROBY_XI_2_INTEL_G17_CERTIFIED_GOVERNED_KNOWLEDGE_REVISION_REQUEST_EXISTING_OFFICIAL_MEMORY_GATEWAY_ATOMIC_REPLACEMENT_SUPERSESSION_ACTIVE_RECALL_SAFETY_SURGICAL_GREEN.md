# ROBY XI.2 — INTEL-G17 — SURGICAL GREEN

## Gate

**CERTIFIED GOVERNED KNOWLEDGE REVISION REQUEST → EXISTING OFFICIAL MEMORY
GATEWAY → EXISTING MEMORY RUNTIME → ATOMIC REPLACEMENT + SUPERSESSION +
ACTIVE-RECALL SAFETY**

## Surgical implementation

G17 reuses the existing Memory authority chain only:

- `OfficialMemoryGateway.apply_governed_knowledge_revision(...)`
- `MemoryRuntimeIntegration.apply_governed_knowledge_revision(...)`
- `CognitiveMemoryStore.apply_governed_revision_atomic(...)`
- existing `CognitiveMemoryRecall`
- existing `OfficialMemoryGateway.recall(...)`

No second Memory gateway, runtime, store, writer, repository, or version authority
was introduced.

## Atomic revision semantics

The existing cognitive store now performs one `BEGIN IMMEDIATE` transaction that:

1. resolves the exact prior memory;
2. verifies category, expected content, and G16 target fingerprint;
3. rejects stale/inactive targets;
4. honors the certified replacement idempotency key;
5. creates one active replacement;
6. marks the prior version `superseded`;
7. persists `supersedes` / `superseded_by` lineage;
8. preserves revision request/proposal/approval/application lineage;
9. commits replacement + supersession together.

An exact replay returns the already-created replacement instead of creating a
second revision. Conflicting idempotency lineage fails closed.

## Recall safety

Productive cognitive recall excludes both `archived` and `superseded` memories.
The official Memory gateway uses the runtime's explicit `active_only=True`
search mode. Raw store search remains available for explicit historical or
introspective use.

## Frozen distinctions

- STALE TARGET != AUTHORIZED TARGET
- REVISION != IN-PLACE EDIT
- SUPERSESSION != ARCHIVE
- REPLACEMENT WRITE != SUPERSESSION
- BOTH MUST COMMIT OR NEITHER COMMITS
- IDEMPOTENT REPLAY != SECOND REVISION
- SUPERSEDED != DELETED
- OLD VERSION MUST REMAIN TRACEABLE
- PRODUCTIVE RECALL MUST USE ACTIVE VERSION
- ONE MEMORY AUTHORITY
