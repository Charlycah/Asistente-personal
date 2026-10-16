# ADR-114 — Mobile Presence Lifecycle

## Status

Accepted.

## Context

M110 declares whether a mobile companion may operate and M111 governs the logical mobile conversation runtime. ROBY still needs a separate representation of whether its mobile presence is inactive, activating, active, backgrounded, dormant, suspending, or terminated.

Conflating presence with the conversation runtime would make application lifecycle, user availability, and operational presence indistinguishable from conversational work.

## Decision

Introduce `core.mobile_presence` as an immutable, repository-backed decision layer over M111.

The lifecycle consumes an M111 decision plus fresh operational signals and emits a declarative transition. It propagates upstream blocked, review-required, and not-applicable states conservatively.

## Invariants

- M111 remains authoritative for conversation runtime state.
- M112 never performs operating-system lifecycle operations.
- Only `ready` decisions are presence-eligible.
- Owner identity must remain coherent with M111.
- Signals must be timezone-aware and fresh.
- Control requests are mutually exclusive.
- Decision identifiers are deterministic and content-derived.
- Requests and decisions are immutable.

## Consequences

Mobile presence can now be reasoned about independently of conversational execution. Notifications, background continuity, voice, sensors, and driving remain outside this milestone.
