# ROBY XI.2 — INTEL-G17 — CONTRACT RED

## Gate

**CERTIFIED GOVERNED KNOWLEDGE REVISION REQUEST → EXISTING OFFICIAL MEMORY
GATEWAY → EXISTING MEMORY RUNTIME → ATOMIC REPLACEMENT + SUPERSESSION +
ACTIVE-RECALL SAFETY**

## Purpose

Expose the post-G16 execution seam without implementing it in CONTRACT RED.

G17 requires the already-existing Memory authority chain to execute one governed
revision as one logical atomic operation. The old version must remain durable and
traceable, the replacement must become active, stale authorization must fail
closed, and superseded knowledge must not re-enter productive recall.

## Required existing-authority seams

- `OfficialMemoryGateway.apply_governed_knowledge_revision(request)`
- `MemoryRuntimeIntegration.apply_governed_knowledge_revision(...)`
- `CognitiveMemoryStore.apply_governed_revision_atomic(...)`

No second Memory gateway, runtime, store, revision writer, or version repository
is permitted.

## Atomic store contract

The store operation must:

1. begin one immediate transaction;
2. resolve the exact target inside that transaction;
3. verify owner-scoped routing through the existing runtime/gateway;
4. verify category, expected current content, and target fingerprint;
5. reject inactive/stale targets;
6. reuse the certified replacement idempotency key;
7. create at most one replacement version;
8. persist replacement metadata as active;
9. persist prior-version metadata as superseded;
10. preserve bidirectional `supersedes` / `superseded_by` lineage;
11. preserve G13/G14/G15/G16 revision lineage;
12. commit replacement + supersession together or neither.

`update_content()` and `archive()` are not valid implementations of intellectual
knowledge revision.

## Productive recall safety

After successful revision:

- superseded v1 remains historically stored;
- superseded v1 is not eligible for productive cognitive recall;
- active v2 remains eligible;
- the official Memory recall path must not surface superseded knowledge as
  current active knowledge.

Historical/introspective access may remain possible through explicit non-
productive paths.

## Frozen distinctions

- REVISION REQUEST != EXECUTION
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

## RED rule

This gate adds tests/documentation only. No production implementation belongs in
CONTRACT RED.
