# ROBY XI.2 — M403.3 Governed Transient Mirror Foundation

**Source baseline:** validated M403.2 — 11,102 tests, Ruff clean, M361 synchronized.

## Objective

Define pure transient-cache semantics for already-admitted synchronization envelopes,
without creating persistence, durable mirroring, merge, replay, memory replication or
knowledge replication.

## Implementation

`core/governed_synchronization/mirror.py` adds:

- `SyncRetentionMode`;
- `SyncRetentionPolicy`;
- `SyncRevisionRelation`;
- `SyncFreshnessState`;
- `SyncMirrorObservation`;
- `sync_state_fingerprint()`;
- `GovernedTransientMirrorEvaluator`.

Only `TRANSIENT_CACHE` is executable. `DURABLE_MIRROR` exists only as an explicit
contractual distinction and fails closed if evaluated.

## Revision semantics

Revision comparison is restricted to one lineage:
source residence, target residence, state domain, source authority, state reference and
compatible schema.

Relations:

- `EMPTY`: no current observation.
- `DUPLICATE`: same revision and same deterministic state fingerprint.
- `ADVANCING`: same lineage and higher revision.
- `STALE`: same lineage and lower revision.
- `CONFLICT`: same revision with different represented state.

Higher revision never grants higher authority. Conflicts never auto-merge or select a
winner.

## Freshness semantics

Each policy defines explicit `fresh_for` and `usable_for` windows:

- `FRESH`;
- `STALE_USABLE`;
- `EXPIRED`.

Expired state is operationally unusable but this foundation does not erase or persist
anything. A revoked source is immediately unusable regardless of freshness or revision.

## Replacement semantics

For the transient-cache decision only:

- `EMPTY` + usable → replacement allowed.
- `ADVANCING` + usable → replacement allowed.
- `DUPLICATE` → no replacement.
- `STALE` → no replacement.
- `CONFLICT` → no replacement / owner review required.
- revoked or expired → no replacement.

This is a pure decision. M403.3 stores no cache object and writes no data.

## Preserved ownership

- M396/M397 remain authoritative for residence/revocation facts.
- M397/M398 remain authoritative for communication/transport.
- Domain owners remain authoritative for represented state.
- M403 only evaluates transient remote representation usability.

## Explicitly out of scope

Disk persistence, repositories, durable mirrors, automatic replay, reconciliation,
merge, conflict winners, memory/knowledge/config replication and credential sync.

## Validation target

M403.3 adds 14 architecture tests. Expected full-suite total: **11,116 tests**.
