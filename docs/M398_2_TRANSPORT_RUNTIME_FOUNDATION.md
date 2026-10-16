# M398.2 — Transport Runtime Foundation

## Status

First operational foundation of **M398 — Governed Physical Transport**.

M398.2 introduces transport-neutral runtime facts only. It creates no socket, TCP
adapter, listener, dialer, serializer, framing implementation, reconnect loop, peer
binding, residence binding, logical session binding or runtime composition wiring.

## Certified inherited baseline

M398.2 starts only from certified M398.1:

- 10,702 tests passed;
- Ruff clean;
- M361 quality baseline synchronized;
- zero known regressions;
- M398-I00 through M398-I14 active.

## Purpose

M398.1 established what a carrier may and may not do. M398.2 gives the future carrier
layer a minimal vocabulary for describing its own runtime condition without borrowing
identity, trust or session semantics from M396/M397.

The new `core.physical_transport` package owns only transport-runtime facts. It is not a
manager, authority, orchestrator, gateway, network stack or connectivity replacement.

## Productive contracts

### `PhysicalTransportId`

Opaque identifier for one configured transport instance. It identifies a transport
configuration only. It is never a `ResidenceId`, peer identity, session identity,
network address or admission credential.

### `PhysicalTransportRuntimeState`

The runtime may report only these carrier facts:

- `UNCONFIGURED` — no physical transport is configured;
- `INACTIVE` — configured but not currently available for I/O;
- `AVAILABLE` — carrier runtime reports ordinary availability;
- `DEGRADED` — carrier runtime reports impaired but observable availability;
- `UNAVAILABLE` — configured carrier cannot currently provide I/O.

These states say nothing about authentication, residence admission, M397 session
lifecycle, connectivity readiness or operational authority.

### `PhysicalTransportRuntimeSnapshot`

Immutable, timestamped observation of one runtime state. Configured states require an
opaque transport id and adapter name. `UNCONFIGURED` forbids both, preventing a phantom
configured carrier from being inferred.

`carrier_available` is deliberately a carrier-only fact. It must never be treated as
M397 `READY`, admission or authorization. `authorizes_action` is permanently false.

### `PhysicalTransportRuntimeBoundary`

Read-only Protocol exposing a snapshot. M398.2 does not provide an implementation and
does not open, close, read or write any physical connection.

## New foundation invariants

### M398-R00 — Runtime Facts Are Not Connectivity Truth

Physical runtime state describes only carrier condition. It never replaces M397
authentication, admission, lifecycle, health/readiness or message contracts.

### M398-R01 — Transport Identity Is Not Peer Identity

`PhysicalTransportId` identifies a configured carrier instance only and cannot be used
as `ResidenceId`, peer identity or `ConnectivitySessionId`.

### M398-R02 — Availability Is Not Readiness

`AVAILABLE` or `DEGRADED` means only that carrier I/O may be physically observable.
It never means a residence is authenticated, admitted or communication-ready.

### M398-R03 — Unconfigured Fails Closed

An `UNCONFIGURED` snapshot cannot carry a transport id or adapter name. Absence of
configuration is explicit rather than inferred as an available default.

### M398-R04 — Runtime Observation Is Read-Only

The M398.2 boundary exposes observations only. It does not create connections, bind
peers, modify sessions, retry I/O or mutate canonical state.

### M398-R05 — No Concrete Carrier Dependency

`core.physical_transport` imports no socket, TCP/HTTP/WebSocket/Bluetooth implementation
and has no dependency on a network library.

### M398-R06 — No Credential Ownership

Runtime snapshots contain no secret, credential, token, key material or path to
`.roby/credentials.json`.

### M398-R07 — No Action Authority

No runtime state authorizes tools, device actions, memory mutation, code execution or
any cognitive operation. `authorizes_action` remains false.

### M398-R08 — Binding Remains Future Work

M398.2 contains no residence, peer or logical-session binding. That responsibility is
reserved for M398.3, where physical facts will be explicitly linked to M397 contracts.

## Deliberately out of scope

M398.2 does not add sockets, TCP, ports, hostnames, addresses, listener/dialer behavior,
framing, serialization, byte buffers, retries, reconnects, discovery, cryptography,
pairing, remote execution, remote file access, memory synchronization or distributed
cognitive execution.

It also performs no change to `app/runtime_root_factory.py` or any other composition
root.

## Exit criterion

M398.2 is complete when the transport-neutral runtime contracts exist, remain free of
physical network dependencies and authority semantics, preserve the M398.1
constitution, synchronize project documentation and quality baseline, and pass Ruff
plus the complete pytest suite with zero regressions.
