# ADR 203 — Cognitive Event Bus

## Decision

ROBY will add a synchronous, governed cognitive event bus immediately after M202. M203 converts the current global cognitive state into immutable, traceable events and dispatches them to owner/session-scoped subscribers without coupling cognitive domains directly.

## Event model

Each event includes:

- owner and session identity;
- event type and source domain;
- topic and bounded value;
- confidence;
- exact source lineage;
- timezone-aware creation time;
- deterministic event identifier.

Supported event types are `state_changed`, `signal_published`, `constraint_raised`, and `health_changed`.

## Delivery model

- Publication is idempotent.
- Retention is bounded per owner/session.
- Subscriptions can filter by event type, topic, and source domain.
- Delivery is synchronous and deterministic.
- Consumer failures are contained and recorded as failed deliveries.
- One failing consumer cannot prevent storage or delivery to other consumers.
- Subscriptions and event history never cross owner/session boundaries.

## Constraints

- M203 requires M201 and M202 in the official composition root.
- M203 does not replace the blackboard; it communicates changes derived from governed state.
- M203 publishes only a traceable delivery receipt back to M201.
- Event delivery does not grant execution authority to consumers.
- M203 cannot execute tools, select providers, mutate memory, rewrite plans, arbitrate priorities, bypass governance, or create commitments.
- Official contributor order is M196, M197, M198, M199, M200, M201, M202, M203, then existing cognitive stages.

## Consequences

M204-M210 receive a stable event surface for cross-domain coordination, scheduling, arbitration, context fusion, health monitoring, optimization, and whole-system integration. The operational runtime remains authoritative and unchanged.
