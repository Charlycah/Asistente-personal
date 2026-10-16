# ROBY XI.2 — M403.2 Governed Synchronization Minimal Transport Wiring

**Source baseline:** validated M403.1 — 11,093 tests, Ruff clean, M361 synchronized.

## Objective

Carry already-admitted M403 synchronization envelopes over the existing M397/M398
governed channel without creating transport, session, persistence, replication or
application authority.

## Implementation

`core/governed_synchronization/channel_adapter.py` adds
`GovernedSynchronizationChannelAdapter`.

The adapter:

- serializes `GovernedSyncEnvelope` deterministically to JSON;
- places that JSON in the opaque `MessagePayloadReference` of an M397
  `AuditableMessageEnvelope`;
- uses the existing `GovernedResidenceChannelBoundary` as carrier;
- verifies session, authenticated peer/source and local target on receipt;
- reconstructs the M403 envelope;
- runs the existing M403 admission boundary;
- returns only `(envelope, admission)`.

It does not persist, apply, merge, queue, retry, broadcast or interpret domain truth.

## Ownership

- M396 owns ResidenceId and residence admission.
- M397 owns session, peer identity, message semantics and readiness.
- M398 owns framing and physical delivery.
- M403 owns only synchronization-state representation and sync admission.

M397 and M398 do not import M403.

## Invariants

- GS-W01: M403 does not own transport.
- GS-W02: M397 retains authentication/session/readiness.
- GS-W03: M398 retains framing/physical delivery.
- GS-W04: envelope source must match the governed/authenticated peer.
- GS-W05: envelope target must match the local ResidenceId.
- GS-W06: peer/session mismatch fails closed.
- GS-W07: receive does not imply admission.
- GS-W08: admission does not imply persistence.
- GS-W09: admission does not imply apply/import.
- GS-W10: admission does not imply cognitive acceptance.
- GS-W11: no implicit forwarding or broadcast.
- GS-W12: no durable queue.
- GS-W13: no M403 retry loop; M398 recovery remains authoritative.
- GS-W14: M397/M398 never depend on M403.
- GS-W15: transport failure never transfers state authority.

## Explicitly out of scope

Persistence, mirroring, merge, conflict resolution, memory replication, knowledge
replication, configuration replication, credential sync, runtime wiring and automatic
background synchronization remain unimplemented.

## Validation target

M403.2 adds 9 architecture tests. Expected full-suite total: **11,102 tests**.
