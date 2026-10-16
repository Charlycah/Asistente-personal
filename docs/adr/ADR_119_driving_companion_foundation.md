# ADR-119 — Driving Companion Foundation

## Status
Accepted

## Context
M106–M116 establish cross-device, mobile, contextual, and hands-free contracts. ROBY needs a governed entry point for driving scenarios without coupling the core to vehicle hardware, navigation, location, or audio execution.

## Decision
Introduce `core.driving_companion` as an immutable decision layer. It consumes the M115 context snapshot and M116 hands-free decision, validates lineage and ownership, and declares one of four logical modes: inactive, passenger, driver-ready, or driver-active.

The engine is conservative about stale or low-confidence context, missing consent, upstream review/block states, and insufficient hands-free operation for a driver.

## Invariants
- M115 remains the authority for mobile context.
- M116 remains the authority for hands-free eligibility.
- Ready is the only status that permits driving-companion operation.
- Decisions are immutable, deterministic, repository-backed, and auditable.
- M117 performs no vehicle, navigation, sensor, audio, Bluetooth, Android Auto, or CarPlay I/O.

## Consequences
Driving-specific runtimes can be added later without changing mobile or hands-free contracts. Execution remains outside this milestone.
