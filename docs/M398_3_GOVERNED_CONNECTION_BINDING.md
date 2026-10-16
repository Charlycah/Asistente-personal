# M398.3 — Governed Connection Binding

## Purpose

Bind physical carrier facts from M398.2 to one already-governed M397 logical
session without allowing the physical layer to create identity, trust, admission,
session lifecycle, readiness or operational authority.

## Permanent binding invariants

- **M398-B00 — Projection only.** `GovernedConnectionBinding` is an immutable
  projection over facts owned elsewhere; it is not a manager or authority.
- **M398-B01 — Configured carrier required.** An unconfigured physical runtime
  cannot participate in a connection binding.
- **M398-B02 — Session coherence.** The adapter-local transport binding must refer
  to the same `ConnectivitySessionId` already integrated by M397.
- **M398-B03 — Residence coherence.** The transport binding must refer to the same
  governed peer residence as the M397 lifecycle snapshot.
- **M398-B04 — Opaque peer reference.** `TransportPeerReference` remains
  adapter-local data and never becomes residence or peer identity.
- **M398-B05 — Physical availability is insufficient.** An available carrier does
  not create M397 authentication, admission, lifecycle state or readiness.
- **M398-B06 — Logical readiness is insufficient.** M397 readiness does not imply
  that a physical carrier is currently available.
- **M398-B07 — Combined communication readiness only.** The binding may report
  communication readiness only when carrier availability and M397 governed
  readiness are both true.
- **M398-B08 — No action authority.** A coherent connection binding never grants
  permission to execute, interpret or promote a received message.
- **M398-B09 — Read-only boundary.** The boundary exposes only the current
  immutable binding or absence of one; it cannot connect, reconnect or mutate
  session/residence state.

## Architectural boundary

M398.3 is the first explicit bridge between `core.physical_transport` and the
logical contracts already certified in M397. It reuses `TransportSessionBinding`
from M397.10 rather than creating a parallel binding vocabulary. Authentication,
admission, session lifecycle and health remain owned by their existing M397
boundaries.

There is still no socket, TCP adapter, listener, dialer, framing, serialization,
network discovery or runtime wiring in this increment. Framing and serialization
of the auditable message envelope are reserved for M398.4.

## Validation

The increment must regenerate M361 and pass Ruff plus the complete pytest suite
without regressions.
