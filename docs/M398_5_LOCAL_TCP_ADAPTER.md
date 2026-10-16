# M398.5 — Local TCP Adapter

## Purpose

Introduce ROBY's first concrete physical carrier while keeping TCP strictly subordinate
to the governed M397/M398 contracts. TCP moves already-framed bytes; it does not decide
identity, authentication, admission, lifecycle, readiness, message meaning or action
authority.

## Permanent TCP invariants

- **M398-T00 — Carrier only.** Local TCP carries bytes and owns no cognitive/domain
  authority.
- **M398-T01 — Endpoint is not identity.** Host and port form only an adapter-local
  `TransportPeerReference`; they never become residence or peer identity.
- **M398-T02 — Existing outbound contract.** Sending consumes the M397.10
  `TransportSendRequest` rather than creating a parallel request model.
- **M398-T03 — Existing framing contract.** TCP sends exactly the bytes produced by
  M398.4 and does not serialize or interpret envelopes itself.
- **M398-T04 — Binding coherence before I/O.** A request whose opaque peer reference
  differs from the configured endpoint is rejected before opening a connection.
- **M398-T05 — Physical failure stays physical.** Connection/send failures become
  transport operation failures and never alter authentication or admission.
- **M398-T06 — Bounded inbound frame.** Incoming length is checked against the M398.4
  maximum before reading a body.
- **M398-T07 — Stream fragmentation is normal.** TCP reads accumulate exactly the
  declared frame bytes and fail closed on premature EOF.
- **M398-T08 — No decode authority.** The TCP adapter returns a serialized frame; the
  M398.4 codec remains the only framing/serialization authority.
- **M398-T09 — No payload interpretation.** TCP never loads or interprets payload
  references or contents.
- **M398-T10 — No action authority.** A successful connection or send never grants
  permission to execute an action.
- **M398-T11 — No lifecycle orchestration.** This increment does not own listeners,
  dialer policy, reconnect loops, discovery, admission or session creation.

## Concrete carrier

`SystemTcpSocketFactory` is the first real physical implementation and uses Python's
standard-library `socket.create_connection`. `LocalTcpAdapter` remains testable through
small socket/factory protocols and can therefore be validated without external network
dependencies.

Outbound sends use one fresh connection and close it after the frame is carried. This
is deliberately minimal. Long-lived listener/dialer lifecycle and governed connection
orchestration are reserved for M398.6.

## Boundary

M398.5 does not make a TCP address trusted. It does not authenticate a peer, admit a
residence, create or revive a logical session, derive M397 readiness, decode message
semantics or authorize execution.

Listener and dialer lifecycle are reserved for M398.6.

## Validation

Regenerate M361 and require Ruff plus the complete pytest suite without regressions.
