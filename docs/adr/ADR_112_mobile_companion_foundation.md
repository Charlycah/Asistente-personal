# ADR 112 — Mobile Companion Foundation

## Status
Accepted.

## Context
M106–M109 establish device identity, capability description, context-transfer manifests, and active-device arbitration. ROBY now needs a mobile-specific operational foundation without prematurely implementing a mobile runtime, background services, voice, notifications, location, or transport.

## Decision
Introduce `core.mobile_companion` as a pure, deterministic, auditable decision layer. It consumes an M109 arbitration decision, the selected mobile endpoint, and its M107 capability match. It evaluates operational constraints and produces a mobile companion foundation describing status, effective mode, enabled modalities, runtime eligibility, and rationale.

Supported modes are foreground, background, hands-free, and passive. Policy governs observation freshness, battery threshold, network and user-presence requirements, and whether background or hands-free operation may be admitted.

## Invariants
- M109 remains authoritative for device selection.
- M107 remains authoritative for capability compatibility.
- The selected endpoint must be mobile and owned by the request owner.
- Only `ready` results are runtime-eligible.
- Enabled modalities are declarations, not executions.
- Results are immutable, deterministic, and repository-auditable.

## Non-goals
M110 does not execute a mobile conversation loop, activate sensors, request permissions, send notifications, capture or synthesize audio, read location, transfer context, or mutate the active session.
