# M397.6 — Session Lifecycle

## Purpose

M397.6 defines the finite logical lifecycle of a governed connectivity session without
opening, owning or closing any real network transport.

## Core rule

> **A session is finite, explicit and observable; it is never ambient connectivity.**

## Lifecycle

A session begins in `CREATED`.

A valid normal progression is:

`CREATED -> ACTIVE -> CLOSING -> CLOSED`

A session may instead move to `TERMINATED` from any non-terminal state when
authentication fails, admission is denied, residence membership is revoked or a
connectivity failure requires safe termination.

`CLOSED` and `TERMINATED` are terminal states and cannot transition further.

## Contracts

### `SessionLifecycleState`

Defines:

- `CREATED`
- `ACTIVE`
- `CLOSING`
- `CLOSED`
- `TERMINATED`

### `SessionTerminationReason`

Provides non-secret reason categories such as local close, peer close, authentication
failure, admission denial, revocation and generic failure.

### `SessionLifecycleSnapshot`

Immutable logical state bound permanently to one `ConnectivitySessionId` and one peer
`ResidenceId`.

A terminal snapshot must contain a termination reason. A non-terminal snapshot cannot
pretend to have one.

### `SessionLifecycleTransition`

Represents and validates a proposed transition between two snapshots.

It guarantees that a lifecycle transition cannot change session identity or peer
residence identity.

It performs no I/O and mutates no runtime state.

## State meaning

`ACTIVE` means only that the logical session lifecycle has reached its active phase.

It does not mean:

- the peer is authenticated;
- the peer is admitted;
- the peer is `READY`;
- a transport is physically connected;
- any command is authorized.

Those remain separate M397 facts.

## Failure and revocation

A failed authentication, denied admission, revocation or connectivity failure may
terminate a logical session. Termination does not alter M396 residence history and does
not revoke the primary home.

## No resurrection

A `CLOSED` or `TERMINATED` session never becomes active again.

Any future reconnection requires a new `ConnectivitySessionId`, new authentication
evaluation and new admission verification.

## Runtime and transport boundary

M397.6 introduces no socket, connection manager, server, client, background task,
timeout loop, heartbeat, transport close operation or runtime wiring.

## Exit criterion

M397.6 is complete when session lifecycle identity and transition rules are immutable,
finite, fail-safe, transport-neutral and regression-tested.

> **ROBY may reconnect to the same residence, but never by resurrecting an old
> session.**
