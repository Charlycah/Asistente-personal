# M397.2 — Connectivity Domain Foundation

## Purpose

M397.2 materializes the smallest productive, transport-neutral vocabulary required to
represent connectivity facts defined by M397.1.

It does **not** open a network connection.

## Authority boundary

`core.connectivity_domain` is a declarative domain model. It can represent:

- a peer residence identity claim;
- a finite logical session identifier;
- observable connectivity state;
- whether authentication has been established;
- whether the peer residence is admitted;
- whether the represented session is ready to communicate.

It cannot:

- authenticate a peer;
- admit or revoke a residence;
- open sockets or choose network addresses;
- send or receive messages;
- execute remote actions;
- synchronize memory or state;
- distribute credentials;
- promote a residence or alter the primary home.

## Contracts

### `PeerIdentityClaim`

Carries a `ResidenceId` claimed by a peer. A claim is deliberately not proof.

### `ConnectivitySessionId`

Provides an opaque logical identity for one finite connectivity relationship. It is not
an IP address, hostname, URL, port or socket identifier.

### `ConnectivityState`

Represents observable connectivity facts:

- `DISCONNECTED`
- `AUTHENTICATED`
- `CONNECTED`
- `READY`
- `DEGRADED`
- `UNAVAILABLE`

These values do not represent residence admission or authority.

### `ConnectivitySessionSnapshot`

Immutable snapshot combining session identity, peer residence identity, observable
state and the independent authentication/admission facts.

`can_communicate` is true only when the peer is authenticated, admitted and `READY`.
It is a communication-readiness fact only. It never authorizes a command or capability.

## Preserved constitutional distinctions

M397.2 preserves:

`ADMITTED != AUTHENTICATED != CONNECTED != READY`

and:

> **Connectivity grants communication; it never grants authority.**

## Transport independence

The domain imports no socket, HTTP, WebSocket, Bluetooth or other transport library.
Concrete adapters remain future work.

## Runtime boundary

M397.2 is not wired into `app/runtime_root_factory.py`. No listener, client, server,
thread, background task, heartbeat or network lifecycle is created.

## Exit criterion

M397.2 is complete when the domain contracts are immutable, transport neutral,
architecture-tested, root documentation is synchronized and the complete project
validation remains clean.
