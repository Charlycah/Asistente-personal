# M397.3 — Peer Identity Contract

## Purpose

M397.3 defines how a future connectivity peer may present a stable logical identity
without confusing declaration, evidence, authentication, admission or network address.

## Core rule

> **A peer may claim an identity; only a governed authentication step may validate it.**

## Contracts

### `PeerIdentityClaim`

Carries only the claimed `ResidenceId`.

### `PeerIdentityDescriptor`

Provides descriptive, transport-neutral metadata such as a human-readable label and an
optional opaque instance hint. It contains no IP, hostname, URL, port, MAC address,
socket identifier, credential or secret.

### `PeerIdentityEvidence`

References opaque evidence associated with the claimed `ResidenceId` and a future
authentication scheme. It does not validate itself and carries no secret material.

### `PeerIdentityPresentation`

Groups claim, descriptor and optional evidence into one immutable presentation. All
parts must refer to the same `ResidenceId`.

## Constitutional distinctions

M397.3 preserves these separations:

- claim != proof;
- evidence reference != authentication result;
- authentication != admission;
- residence identity != network address;
- peer presentation != authorization;
- successful future authentication != permission to execute.

## Transport independence

No peer identity contract contains IP, hostname, URL, port, socket, transport session,
Bluetooth address or interface details.

A residence may reconnect through a different network path and remain the same logical
peer.

## Security boundary

M397.3 introduces no cryptographic algorithm, private/public key, certificate parsing,
token exchange, pairing secret, credential store or authentication verifier.

Those belong to a future governed authentication boundary.

## Authority boundary

The peer identity models are immutable data. They cannot authenticate, admit, revoke,
execute, send, receive, connect, synchronize or alter residence roles.

## Runtime boundary

M397.3 introduces no runtime wiring and no network activity.

## Exit criterion

M397.3 is complete when peer identity presentation is internally consistent, transport
neutral, free of secret-bearing fields and architecture-tested against M396/M397
invariants.
