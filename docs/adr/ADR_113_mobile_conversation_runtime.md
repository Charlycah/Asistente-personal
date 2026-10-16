# ADR-113 — Mobile Conversation Runtime

## Status
Accepted.

## Context
M110 declares whether a mobile companion may operate and which modalities are eligible. ROBY still needs a channel-neutral logical runtime that governs the lifecycle of a mobile conversation without performing device I/O.

## Decision
Introduce `core.mobile_runtime` as an immutable, repository-backed state-transition layer. It consumes an M110 foundation and explicit runtime signals, then emits a deterministic decision across idle, running, waiting-user, background, suspended, and terminated states.

The runtime may recommend start, resume, wait, enter-background, suspend, stop, or no action. It does not perform the action.

## Invariants
- M110 remains the authority for mobile eligibility and effective mode.
- Owner identity must match the M110 foundation.
- Runtime control requests are mutually exclusive.
- Stale or future-dated observations require review.
- Only ready decisions are runtime-eligible.
- Decisions and identifiers are immutable and deterministic.

## Boundaries
M111 does not invoke STT/TTS, notifications, sensors, location, transport, timers, networks, or session mutation. It does not deliver messages or change the active device.
