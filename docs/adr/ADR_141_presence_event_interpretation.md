# ADR-141 — Presence Event Interpretation

## Status
Accepted

## Context
M138 provides governed anonymous presence-change records downstream from M137 continuity. Higher layers require normalized semantic events, but interpretation must remain separate from detection, personal inference, decision-making, and automation.

## Decision
Introduce `core.presence_event_interpretation` as the sole M139 domain boundary downstream from M138.

M139:

- accepts only immutable `PresenceChangeDetectionResult` inputs;
- validates ownership, freshness, confidence, limits, deduplication, ordering, and ambient-context lineage;
- maps each M138 change kind to one normalized anonymous ambient meaning;
- suppresses M138 no-change outcomes as explicit `NO_EVENT` results;
- preserves the exact M134 → M135 → M136 → M137 → M138 → M139 lineage;
- stores immutable interpretation results through a repository protocol.

M139 does not detect changes, compare presence samples, recompute continuity, infer identity, activity or intent, count people precisely, track individuals or movement, access sensors, invoke providers, mutate the platform, decide responses, or automate actions.

## Consequences
The Ambient Context domain gains a deterministic semantic event boundary. Future integration layers can consume normalized anonymous presence meanings without coupling interpretation to observation, detection, cognition, conversation, or execution.
