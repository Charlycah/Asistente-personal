# M398.9 — Security & Abuse Guardrails

## Purpose

Add mandatory end-to-end transport guardrails for message replay, timestamp abuse and
governed residence/session mismatches without granting the transport layer any new
identity, authentication, admission, lifecycle or action authority.

## Permanent security invariants

- **M398-SG00 — Guard before acceptance.** An inbound message is not exposed by the
  secure channel until it passes the transport-security guard.
- **M398-SG01 — Replay rejection.** Repeated `MessageId` values within the bounded
  replay window are rejected fail-closed.
- **M398-SG02 — Bounded replay memory.** Anti-replay state has an explicit maximum
  size and cannot grow without bound.
- **M398-SG03 — Stale-message rejection.** Messages older than the configured maximum
  age are rejected.
- **M398-SG04 — Future-skew rejection.** Messages beyond configured clock skew are
  rejected.
- **M398-SG05 — Session coherence.** Security assessment requires the M397 session id
  already bound to the channel.
- **M398-SG06 — Sender coherence.** Security assessment requires the governed remote
  residence as sender.
- **M398-SG07 — Receiver coherence.** The message must target the configured local
  ROBY residence.
- **M398-SG08 — Security acceptance is not execution authority.** Passing every
  guardrail still never authorizes an action.
- **M398-SG09 — Existing channel remains authoritative for transport.** Security wraps
  M398.8 rather than defining another TCP/framing path.
- **M398-SG10 — No authentication duplication.** Security guardrails do not
  authenticate peers or admit residences; M397 remains authoritative.
- **M398-SG11 — Closure remains separate.** Cross-stage integration audit and formal
  closure remain reserved for M398.10.

## Guard model

`GovernedMessageSecurityGuard` owns only bounded anti-replay and temporal/message
coherence checks. `SecureGovernedResidenceChannel` makes that guard mandatory for
messages exposed through the secure receive path.

The replay cache is deliberately bounded and evicts oldest accepted message ids when
its configured capacity is exceeded. This prevents an unbounded memory-growth path in
the transport security layer.

Timestamp validation operates only on the auditable envelope metadata. It neither
interprets payload content nor creates cryptographic identity semantics.

## Explicit exclusions

M398.9 does not introduce encryption, public-key infrastructure, certificates, remote
execution, capability delegation, memory replication or distributed cognition. It
also does not replace M397 authentication/admission or M398.4 framing limits.

M398 integration audit and formal closure are reserved for M398.10.

## Validation

The two pending M398.8 Ruff import-order corrections are integrated into this baseline.
Regenerate M361 and require Ruff plus the complete pytest suite without regressions.
