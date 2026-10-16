# M398.8 — End-to-End Residence Channel

## Purpose

Compose the already-governed M397/M398 building blocks into one explicit residence
channel capable of carrying `AuditableMessageEnvelope` instances end-to-end over an
established TCP carrier without creating any new identity, trust, session, execution
or cognitive authority.

## Permanent end-to-end invariants

- **M398-E2E00 — Composition only.** The channel composes existing binding, framing,
  carrier and connectivity facts; it does not replace their authorities.
- **M398-E2E01 — Carrier/binding coherence.** The active TCP peer reference must match
  the `GovernedConnectionBinding` before a channel can exist.
- **M398-E2E02 — Readiness is inherited.** Channel readiness comes only from the
  already-governed binding and cannot be created by a live socket.
- **M398-E2E03 — No send while not ready.** Outbound transport fails closed unless
  the governed binding is communication-ready.
- **M398-E2E04 — Existing send contract reused.** Outbound envelopes are validated
  through M397.10 `TransportSendRequest`.
- **M398-E2E05 — Existing framing reused.** The channel sends only bytes produced by
  the M398.4 codec and does not define another wire schema.
- **M398-E2E06 — Inbound session coherence.** A received envelope must belong to the
  logical session already bound to the channel.
- **M398-E2E07 — Inbound peer coherence.** A received envelope sender must equal the
  governed remote residence.
- **M398-E2E08 — EOF is physical only.** Physical EOF yields no message and does not
  mutate M397 lifecycle.
- **M398-E2E09 — Close is physical only.** Closing the channel closes the carrier, not
  the logical session or residence state.
- **M398-E2E10 — No action authority.** Channel existence, readiness and valid message
  receipt never authorize execution.
- **M398-E2E11 — No distributed cognition.** Remote tool execution, memory
  replication, cognitive routing and capability delegation remain outside M398.8.

## End-to-end path

Outbound:

`GovernedConnectionBinding -> TransportSendRequest -> M398.4 codec -> TCP carrier`

Inbound:

`TCP carrier -> bounded M398.5 frame read -> M398.4 decode -> session/residence checks`

This is the first place where the physical transport path and the M397 logical
governance path meet in one reusable channel object. The meeting point remains a
projection/composition layer, not a new manager or authority.

## Explicit exclusions

M398.8 does not add remote execution, remote tools, memory synchronization, state
replication, distributed planning, discovery, cloud relay or autonomous reconnection.
Security and abuse guardrails for the end-to-end channel are reserved for M398.9.

## Validation

Regenerate M361 and require Ruff plus the complete pytest suite without regressions.
