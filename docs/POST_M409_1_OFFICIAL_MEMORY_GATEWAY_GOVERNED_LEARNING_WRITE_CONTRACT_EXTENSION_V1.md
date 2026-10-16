# Post-M409.1 — OfficialMemoryGateway Governed Learning Write Contract Extension v1

## Status

IMPLEMENTED / CERTIFICATION PENDING USER GATES.

## Purpose

Extend the existing `OfficialMemoryGateway` with a governed-learning write
operation while preserving the legacy `remember(MemoryItem)` behavior.

The productive write contract is now:

`GovernedMemoryWriteRequest -> OfficialMemoryGateway.remember_governed_learning`
`-> MemoryRuntimeIntegration.store_governed_learning`
`-> CognitiveMemoryStore.store_candidate_idempotent`.

## Semantics

Governed learning v1 is limited to approved preference learning. It persists as
`LearningCategory.USER_PREFERENCE`, preserves the request confidence, uses the
reason `governed_human_approved_learning`, and stores stable tags for governed,
human-approved preference learning. Scope and full lineage remain metadata.

Legacy `remember(MemoryItem)` continues to use `store_explicit` and therefore
retains `STABLE_KNOWLEDGE`, confidence `1.0`, `explicit_user_memory_request`,
and the legacy tags.

## Idempotency

The canonical `CognitiveMemoryStore` adds an internal idempotency table keyed by
the deterministic request idempotency key. `store_candidate_idempotent` uses a
`BEGIN IMMEDIATE` transaction, returning the existing memory id when the key was
already materialized. The existing cognitive-memory schema version remains 1.

This is internal persistence support in the existing store, not a new memory
store or authority.

## Governance

No new gateway, writer, database, Learning authority, Curiosity authority,
conversation wiring, networking, Residential capability or background process
is introduced. Productive automatic invocation from conversation remains out of
scope pending a separate wiring gate.
