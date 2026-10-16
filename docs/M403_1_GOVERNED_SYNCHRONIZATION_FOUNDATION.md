# M403.1 — Governed Synchronization Foundation

## Scope

Minimal contractual foundation only. M403.1 introduces an immutable synchronization
envelope and a pure fail-closed admission boundary. It does not transport, persist,
merge, replicate or apply remote state.

## Models

- `SyncShareabilityClass`: `LOCAL_ONLY`, `SHAREABLE`, `TRANSIENT`, `MIRRORABLE`, `PROHIBITED`.
- `GovernedSyncEnvelope`: directed state representation preserving ResidenceId, source authority, revision, schema and lineage.
- `GovernedSyncAdmission`: immutable `ADMITTED` / `REJECTED` result with checks and limitations.
- `GovernedSynchronizationAdmission`: pure admission boundary.

## Preserved ownership

- M396 remains owner of residence identity/admission.
- M397/M398 remain owners of connectivity and physical transport.
- Domain authorities remain owners of synchronized state.
- M403 owns only synchronization representation/admission semantics.

## Invariants

- envelope != authority;
- receive != persist;
- persist != apply;
- revision != winner;
- timestamp != authority;
- LOCAL_ONLY never crosses the boundary;
- PROHIBITED always fails closed;
- MIRRORABLE is not yet authorized;
- credentials/secrets never enter synchronization payloads;
- no implicit broadcast;
- no implicit replication.

## Out of scope

No sync runtime, registry, repository, merge engine, memory replication, knowledge
replication, configuration replication, credential synchronization, transport wiring or
automatic application is introduced.
