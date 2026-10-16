# ADR 111 — Active Device Arbitration

## Status
Accepted.

## Context
M106 establishes device identity and session continuity, M107 describes device
capabilities, and M108 prepares auditable context-transfer manifests. ROBY still
needs a deterministic, conservative decision about which eligible device should
be considered active for a session.

## Decision
Introduce `core.device_arbitration`. The component evaluates immutable device
candidates and emits an auditable decision with status, action, selected device,
previous device, candidate scores and rationale.

The arbitrator considers ownership, endpoint availability and authentication,
observation freshness, device trust, capability-match status, user preference,
current-device stability, switch margin and—when switching—a ready M108 transfer
manifest.

## Invariants
- M106 remains authoritative for identity and session continuity.
- M107 remains authoritative for capability compatibility.
- M108 remains authoritative for transfer-manifest readiness.
- M109 only selects an eligible device; it never activates it.
- Inputs and decisions are immutable and deterministic for equal input and time.
- Ambiguity or stale evidence is surfaced as review, not silently accepted.

## Non-goals
M109 does not mutate sessions, transport context, open connections, discover
hardware, request permissions, deliver messages or implement Mobile Companion.
