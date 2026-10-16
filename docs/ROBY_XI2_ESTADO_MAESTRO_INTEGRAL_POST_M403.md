# ROBY XI.2 — Estado Maestro Integral Post-M403

## 1. Official baseline

**M403.3 — Governed Transient Mirror Foundation**

Certification:
- M361 synchronized.
- Ruff clean.
- 11,116 tests passed.
- 0 known regressions.

## 2. Current master-trunk state

- M401 — Governed Cognitive Use of External Evidence: CLOSED.
- M402 — Residential Node: CLOSED architecturally and operationally.
- M403 — Governed Synchronization: CLOSED architecturally and at the minimal operational level required by the master plan.
- Residential Node Physical Deployment Certification: PENDING, non-architectural.
- Residential Perception Foundation: NEXT MASTER GATE.

## 3. Governed Synchronization closed chain

M403.1:
- explicit shareability taxonomy;
- immutable `GovernedSyncEnvelope`;
- fail-closed `GovernedSyncAdmission`;
- source/target ResidenceId;
- source-authority preservation;
- credential/secret exclusion.

M403.2:
- reuses M397 session/message contracts;
- reuses M398 physical transport;
- source peer and target-local identity consistency;
- receive/admit only, no persistence or apply.

M403.3:
- explicit transient retention policy;
- deterministic state fingerprint;
- lineage-scoped revision relations;
- EMPTY / DUPLICATE / ADVANCING / STALE / CONFLICT;
- FRESH / STALE_USABLE / EXPIRED;
- revocation-aware usability;
- no automatic merge/replay/reconciliation.

## 4. Permanent synchronization decisions

### Shareability
- `LOCAL_ONLY`: never crosses the sync boundary.
- `SHAREABLE`: may be transported as a subordinate read-only representation.
- `TRANSIENT`: may travel but is not durable by default.
- `MIRRORABLE`: conceptual future category; durable execution not authorized.
- `PROHIBITED`: always fail closed.

### Memory
Authoritative memory remains local to its existing owner. No generic memory replication is authorized.

### Knowledge
Authoritative knowledge remains local to its existing owner. No generic knowledge replication is authorized.

### Configuration
No implicit configuration replication. Any future shared configuration requires a specific domain policy and a separate Go/No-Go.

### Credentials
Credentials, tokens, secrets and private keys are not synchronizable state.

### Conflicts/versioning
M403 may identify duplicate, advancing, stale or conflicting revisions within one lineage.
It never decides domain truth, performs semantic merge or selects a winner.

### Recovery
For transient synchronized state, recovery is re-observation after reconnection, not
automatic history replay or reconciliation. M398 retains bounded transport recovery.

## 5. Preserved ownership

- M396: ResidenceId, admission/revocation, capabilities.
- M397: authentication, peer/session/readiness, communication semantics.
- M398: framing, physical transport, bounded transport recovery.
- M402: residential representation/bootstrap.
- Domain owners: authoritative state truth.
- M403: synchronization representation/admission/transport adaptation/transient evaluation only.

## 6. Deferred, non-blocking capabilities

The following are explicitly deferred and do not block M403 closure:
- durable mirror repository/database;
- memory replication;
- knowledge replication;
- configuration replication;
- durable offline queue;
- automatic replay;
- reconciliation engine;
- semantic merge;
- distributed cognitive execution.

A future need may reopen one of these as a new scoped decision, but not as automatic M403 continuation.

## 7. Next master-trunk item

**Residential Perception Foundation**

The next gate must audit how IP cameras, sensors and physical home sources can enter ROBY
initially read-only through the already-governed residence/connectivity/transport/node/
synchronization chain, preserving provenance, permissions, observability and fail-safe
behavior.

No camera/sensor code is authorized before that Go/No-Go.

## 8. Continuity rule

The master direction remains:

distributed residence → connectivity → physical transport → residential node →
governed synchronization → residential perception.

M403 closes the synchronization step. Do not reopen it merely because durable replication
is imaginable. New work must prove that a deferred capability is required by a concrete
consumer and must preserve one ROBY / one brain / one authority per capability.
