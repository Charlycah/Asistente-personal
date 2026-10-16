# ADR-140 — Presence Change Detection

## Status
Accepted

## Context
M136 produces anonymous presence understanding and M137 evaluates temporal continuity between those governed results. The Ambient Context domain now requires a boundary that determines whether an M137 outcome represents a publishable ambient change, while preserving strict separation from identity, activity, movement, sensors, and automation.

## Decision
Introduce `core.presence_change_detection` as the sole M138 domain boundary downstream from M137.

M138:

- accepts only immutable `PresenceContinuityResult` inputs;
- validates owner, freshness, confidence, limits, deduplication, ordering, and ambient-context lineage;
- publishes appearance, disappearance, occupancy variation, transient variation, uncertain variation, and continuity-break events;
- suppresses stable continuity as an explicit no-change result;
- preserves the exact M134 → M135 → M136 → M137 → M138 lineage;
- stores immutable detection results through a repository protocol.

M138 does not compare raw presence samples, reinterpret M136 evidence, identify people, count people precisely, infer activity, track individuals or movement, access sensors, invoke providers, or automate actions.

## Consequences
The architecture gains a deterministic change-event boundary without duplicating M137 continuity logic. Downstream milestones can consume explicit anonymous ambient change records while invasive or action-oriented capabilities remain structurally unavailable.
