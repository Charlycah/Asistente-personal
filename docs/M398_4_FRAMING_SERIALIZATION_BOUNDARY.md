# M398.4 — Framing & Serialization Boundary

## Purpose

Define a deterministic, bounded and fail-closed physical representation for the
already-governed `AuditableMessageEnvelope` without creating network I/O, payload
execution semantics or a second authority.

## Permanent framing invariants

- **M398-F00 — Envelope only.** Framing serializes the M397.9 envelope metadata and
  its opaque payload reference; it does not load, interpret or execute payload contents.
- **M398-F01 — Deterministic encoding.** Equal envelopes produce identical bytes.
- **M398-F02 — Explicit schema version.** Every frame body carries one supported
  schema version and unknown versions are rejected.
- **M398-F03 — Bounded body.** The encoded body has an explicit maximum size.
- **M398-F04 — Explicit framing.** A fixed-width length prefix must match the body
  exactly before deserialization proceeds.
- **M398-F05 — UTF-8 and JSON validation.** Invalid external bytes fail closed.
- **M398-F06 — Exact schema.** Missing or unexpected top-level fields are rejected.
- **M398-F07 — Exact payload-reference schema.** Payload references may contain only
  the canonical `content_type` and `reference` fields.
- **M398-F08 — Domain reconstruction.** Decoding reconstructs the existing M397
  value objects so their invariants are re-applied rather than bypassed.
- **M398-F09 — No authorization.** A valid frame or successfully decoded envelope
  never grants permission to execute an action.
- **M398-F10 — Pure codec boundary.** The codec exposes only encode/decode and owns
  no socket, connection, listener, dialer, session or residence mutation.
- **M398-F11 — Transport independence.** The representation does not depend on TCP,
  HTTP, WebSocket, Bluetooth or any concrete carrier.

## Representation

M398.4 uses canonical JSON encoded as UTF-8 for the frame body, with sorted keys and
compact separators. The body is preceded by a four-byte unsigned big-endian length.
The schema version is `1`, and the configured maximum body size is 65,536 bytes.

This representation is a reference codec behind `MessageFrameCodecBoundary`; future
code may replace the concrete codec without changing M397 identity, admission, session
or message authority.

There is still no socket, TCP adapter, listener or dialer in this increment. The first
concrete local TCP carrier remains reserved for M398.5.

## Validation

The increment must regenerate M361 and pass Ruff plus the complete pytest suite without
regressions.
