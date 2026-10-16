# ADR 206 — Executive Arbitration

## Status
Accepted.

## Context
M201-M205 provide shared signals, global state, event propagation, cross-domain coordination, and a deterministic cognitive schedule. ROBY still needs a governed executive boundary that decides which scheduled cognitive tasks may proceed, which must wait, and which must be rejected before downstream execution.

## Decision
Introduce `ExecutiveArbitrator` as a deterministic, session-scoped executive decision layer. It consumes the latest M205 schedule and produces immutable task dispositions: `authorize`, `defer`, or `reject`.

The arbitrator:

- preserves owner/session isolation;
- fails closed when M205 is unavailable;
- preserves blocking constraints by rejecting blocked tasks;
- authorizes governance repair before dependent work when attention is required;
- publishes only an executive decision record to M201;
- does not execute contributors, invoke tools, select providers, mutate memory, or bypass existing permission and consent controls.

## Consequences
M207 and later milestones can consume a single explicit executive decision rather than infer authority from schedules. Runtime ordering becomes `M201 -> M202 -> M203 -> M204 -> M205 -> M206`.
