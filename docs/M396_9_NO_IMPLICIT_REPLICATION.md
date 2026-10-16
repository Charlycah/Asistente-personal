# M396.9 — No Implicit Replication Guardrails

## Invariant

**M396-I09 — No Implicit Replication**

A residence becoming known, admitted, available, or active does not replicate ROBY's
state. Distributed Residence describes where the same ROBY may be present; it does not
silently copy memory, conversations, databases, files, configuration, credentials, or
cognitive state between localities.

## Rules

1. Explicit admission creates membership, not a replication contract.
2. `AVAILABLE` presence creates reachability context, not data synchronization.
3. `InteractionLocality` changes where an interaction occurs, not where state is copied.
4. `PresenceEndpoint` exposes a window of presence, not a storage replica.
5. Residence Domain owns no replicate, synchronize, mirror, clone, copy-state, backup,
   restore, export, import, push, pull, merge, or conflict-resolution API.
6. Residence Domain owns no replica metadata, replication cursor, sync token, version
   vector, journal, checkpoint, or distributed database contract.
7. `.roby`, credentials, memory stores, conversations, SQLite/database files, project
   data, notes, objectives, configuration, and learned state are never implicitly moved.
8. Any future state distribution must be introduced by a separate governed contract,
   with explicit scope, authority, consent/security, conflict policy, auditability, and
   rollback behavior.
9. M396.9 introduces no transport, RPC, network protocol, cloud dependency, remote
   persistence, or distributed database.
10. I03-I08 remain binding.

## Architectural meaning

The mini-PC, cellular device, or Web can become another authorized place from which
ROBY is present without receiving a hidden copy of ROBY. Presence and replication are
independent architectural concepts.

**More places do not imply more copies.**
