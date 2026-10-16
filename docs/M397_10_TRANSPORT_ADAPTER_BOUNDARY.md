# M397.10 — Transport Adapter Boundary

## Purpose

M397.10 defines the exact boundary between governed connectivity contracts and any
future concrete communication transport.

It introduces no real network implementation.

## Core rule

> **Transport moves messages; it does not define identity, trust or authority.**

## Contracts

### `TransportPeerReference`

Opaque adapter-local reference to a remote communication endpoint.

It may eventually correspond to a socket handle, URL, connection object or another
transport-specific value, but the core treats it only as an opaque reference.

It is not a `ResidenceId`.

### `TransportSessionBinding`

Explicitly binds:

- logical `ConnectivitySessionId`;
- logical peer `ResidenceId`;
- adapter-local `TransportPeerReference`.

The binding prevents transport-local identity from replacing logical residence identity.

### `TransportSendRequest`

Combines a session binding with an `AuditableMessageEnvelope`.

The request is valid only when:

- binding session equals envelope session;
- binding residence equals envelope receiver.

### `TransportOperationDisposition`

Adapter outcomes are explicit:

- `ACCEPTED`
- `REJECTED`
- `UNAVAILABLE`
- `FAILED`

`ACCEPTED` means only that the transport accepted the delivery attempt.

It does not mean the receiver trusted, authorized, executed or even semantically
accepted the message.

### `TransportOperationResult`

Immutable outcome of a transport operation.

`accepted` reflects transport acceptance only.

### `OutboundTransportAdapter`

Protocol boundary for carrying an already-governed outbound envelope.

### `InboundTransportAdapter`

Protocol boundary for exposing a decoded inbound envelope.

Neither adapter owns message authorization, authentication, admission or capability
execution.

## Boundary ownership

Transport adapters may eventually own:

- connection handles;
- byte encoding/decoding;
- framing;
- retry policy explicitly assigned to transport;
- protocol-specific errors.

Transport adapters may not own:

- `ResidenceId`;
- admission decisions;
- authentication authority;
- session governance;
- readiness policy;
- command authorization;
- cognitive authority;
- primary-home selection.

## Transport independence

M397 core contracts remain independent of TCP, HTTP, WebSocket, Bluetooth, USB or any
future mechanism.

A future adapter may import a concrete transport library. `core.connectivity_domain`
must not require that library merely to define its logical contracts.

## Message boundary

The adapter transports `AuditableMessageEnvelope`.

It does not reinterpret `MessageKind.REQUEST` as permission to act.

Receiving a valid envelope remains distinct from authorizing its semantic request.

## Failure boundary

Transport failure may produce `REJECTED`, `UNAVAILABLE` or `FAILED`.

Those outcomes are evidence for higher connectivity layers. They do not directly revoke
residence membership or alter ROBY's primary home.

## Runtime boundary

M397.10 defines adapter protocols only.

It introduces no concrete socket, HTTP client/server, WebSocket implementation,
listener, port, network address, background loop or runtime wiring.

## Exit criterion

M397.10 is complete when logical connectivity can depend on adapter protocols without
depending on any specific network technology, and architecture tests prove that
transport cannot absorb identity, authority or admission semantics.

> **ROBY now has a doorway for transport without letting transport redesign the
> house.**
