# ADR-120 — Driving Context Awareness

## Status
Accepted

## Context
M117 establishes whether ROBY may operate as a driving companion, but eligibility alone does not describe the moment-to-moment cognitive demand of a driving situation. Future interaction layers need a stable context contract without coupling to maps, navigation, vehicle hardware, sensors, or platform APIs.

## Decision
Introduce `core.driving_context` as an immutable awareness layer over the M117 decision. It accepts declarative motion, maneuver, traffic, visibility, attention, passenger, emergency, confidence, and freshness signals and produces a governed contextual-load snapshot.

## Invariants
- M117 remains the sole authority for Driving Companion eligibility and mode.
- M118 describes context; it does not acquire signals or execute interaction.
- Non-ready snapshots cannot permit speech or proactive interaction.
- Emergency and critical-load contexts are conservative.
- Outputs are deterministic, immutable, auditable, and repository-backed.

## Consequences
Later driving interaction, maps, visual, ambient, and unified-companion layers gain a shared context contract while remaining decoupled from the acquisition source. No future domain is pre-implemented or constrained to a specific platform.
