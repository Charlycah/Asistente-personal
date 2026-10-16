# M398.6 — Governed Listener & Dialer

## Purpose

Give the local TCP carrier an explicit inbound/outbound physical lifecycle without
allowing connection establishment to become identity, authentication, admission,
logical-session creation, readiness or operational authority.

## Permanent listener/dialer invariants

- **M398-L00 — Physical lifecycle only.** Listener and dialer own only physical TCP
  connection establishment and closure.
- **M398-L01 — Dial is not authentication.** A successful outbound connection proves
  only physical reachability.
- **M398-L02 — Accept is not admission.** An accepted socket is not a recognized or
  admitted ROBY residence.
- **M398-L03 — Address remains opaque.** The remote TCP address becomes only a
  `TransportPeerReference`; it never becomes `ResidenceId` or peer identity.
- **M398-L04 — No logical-session creation.** Dial/accept cannot create a
  `ConnectivitySessionId` or transition M397 lifecycle.
- **M398-L05 — No session revival.** Opening a new physical carrier never restores a
  closed or terminated logical session.
- **M398-L06 — Explicit listener lifecycle.** Listener open, accept and close are
  separate operations with fail-fast state checks.
- **M398-L07 — Deterministic physical close.** Closing a carrier or listener affects
  only the physical resource.
- **M398-L08 — Existing TCP seams reused.** Outbound dial reuses the M398.5
  `TcpSocketFactoryBoundary`; no parallel client stack is introduced.
- **M398-L09 — Testable server seam.** Listening uses a minimal server-socket factory
  boundary while the concrete implementation remains Python stdlib TCP.
- **M398-L10 — No action authority.** Listener, dialer and accepted/dialed carriers
  always report `authorizes_action = False`.
- **M398-L11 — No recovery policy.** Automatic retry, backoff, reconnect policy,
  failure recovery and logical-session consequences remain outside this increment.

## Concrete lifecycle

`LocalTcpDialer` performs one explicit outbound dial and returns a
`TcpCarrierConnection`. `LocalTcpListener` opens one configured server socket, accepts
one physical connection at a time and exposes the remote address solely as an opaque
transport peer reference.

`SystemTcpServerSocketFactory` is the concrete stdlib implementation for bind/listen
and uses `SO_REUSEADDR` for controlled local restart behavior. It does not inspect
messages or any M397 identity/governance state.

## Authority boundary

M398.6 does not authenticate peers, verify residence membership, create admissions,
create or revive logical sessions, derive readiness, decode messages or authorize
actions. Physical reconnect is therefore only a new carrier event; any future logical
session must pass the M397 gates independently.

Transport failure/recovery policy, retry/backoff and reconnect consequences are
reserved for M398.7.

## Validation

The M398.5 corrected import file is integrated in this baseline. M361 must be
regenerated and the increment must pass Ruff plus the complete pytest suite without
regressions.
