# ADR-123 — Driving Safety Coordination

## Status
Accepted.

## Context
M118 describes driving load, M119 defines the permitted interaction envelope, and M120 defines the conversational form. A final domain boundary is required before any future realization, voice, notification, navigation, or cross-domain integration can consume those outputs.

## Decision
Introduce `core.driving_safety_coordination` as a deterministic, immutable, repository-backed coordinator over the exact M118–M120 lineage.

The coordinator applies the most restrictive upstream result, verifies ownership and identifier lineage, classifies a final safety level, and emits declarative permissions for conversation, voice, initiative, complex dialogue, interruptions, notifications, confirmation, deferral, and emergency override.

## Invariants
- M121 never recalculates driving context, interaction policy, or conversational adaptation.
- Upstream blocked, review-required, deferred, and non-applicable states propagate conservatively.
- Critical load blocks non-emergency interaction.
- Emergency override is explicit, policy-controlled, minimal, and restricted to emergency system alerts.
- A permission cannot be granted unless all upstream contracts allow it.
- Input lineage, ownership, immutability, determinism, and auditability are mandatory.

## Consequences
The Driving domain exposes a stable terminal safety decision without coupling Maps, Visual Understanding, Ambient Context, voice execution, or Unified Companion to internal Driving milestones.

## Non-responsibilities
M121 does not generate text, synthesize or recognize speech, deliver notifications, schedule deferred content, mutate conversation state, control devices, access maps or routing, read sensors, or operate vehicle systems.
