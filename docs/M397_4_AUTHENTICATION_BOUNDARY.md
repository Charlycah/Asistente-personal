# M397.4 — Authentication Boundary

## Purpose

M397.4 defines the governed boundary that may evaluate a peer identity presentation
and produce an explicit authentication result.

It still does not choose or implement cryptography.

## Core rule

> **Authentication validates identity evidence; it does not admit, authorize or
execute.**

## Contracts

### `AuthenticationDisposition`

The result is one of:

- `VERIFIED`
- `REJECTED`
- `INDETERMINATE`

No implicit truth value or network state is used as authentication.

### `PeerAuthenticationRequest`

Carries a finite connectivity `session_id` and the `PeerIdentityPresentation` that must
be evaluated.

### `PeerAuthenticationResult`

Carries the session, logical `ResidenceId`, explicit disposition and optional references
to evidence scheme/reason. It contains no password, secret, private key or credential.

`authenticated` is true only for `VERIFIED`.

### `PeerAuthenticationBoundary`

A protocol defining one operation: evaluate an authentication request and return a
result. M397.4 supplies no concrete evaluator.

## Authority boundary

Authentication has exactly one competence: assess identity evidence.

It cannot:

- create residence admission;
- revoke residence membership;
- make a peer `READY`;
- grant capability authority;
- authorize a message as a command;
- execute remote code;
- distribute credentials;
- promote or migrate the primary home.

## Authentication is not admission

A peer can be `VERIFIED` and still be unadmitted. M396 remains authoritative for
residence admission and revocation.

## Failure semantics

`REJECTED` means the presented identity evidence failed the governed evaluation.

`INDETERMINATE` means the boundary cannot establish a verified identity from the
available evidence. It must never be silently upgraded to `VERIFIED`.

## Security and transport neutrality

M397.4 introduces no:

- hashing/signature algorithm;
- TLS/SSL policy;
- certificate parser;
- public/private key;
- token exchange;
- pairing secret;
- network address;
- socket/HTTP/WebSocket transport;
- credential store.

A future implementation must sit behind `PeerAuthenticationBoundary`.

## Runtime boundary

No authentication implementation is wired into the runtime root in M397.4.

## Exit criterion

M397.4 is complete when authentication input/output and authority limits are explicit,
transport neutral, secret-free, immutable and regression-tested.

> **ROBY can now represent an authentication decision without pretending to know how
> the proof will eventually be verified.**
