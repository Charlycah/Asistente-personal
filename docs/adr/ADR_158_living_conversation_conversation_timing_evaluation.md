# ADR-158 — Living Conversation Conversation Timing Evaluation

## Status
Accepted

## Context
M155 produces a canonical governed conversation candidate but intentionally does not determine whether the present moment belongs to an explicit temporal window. ROBY requires a separate declarative boundary before later timing selection, authorization, realization, and execution.

## Decision
Add M156 as a pure temporal-viability evaluation layer downstream from M155.

M156:

- consumes immutable M155 candidate results;
- selects the best valid candidate deterministically;
- evaluates optional explicit `not_before` and `expires_at` boundaries against a timezone-aware evaluation instant;
- declares `TIMELY`, `TIMELY_PARTIAL`, `DEFERRED`, or `NOT_TIMELY` outcomes;
- preserves the exact M155 candidate and M150 opportunity objects;
- applies owner, freshness, confidence, partial-context, deduplication, and result-limit governance;
- produces deterministic immutable timing-evaluation identifiers;
- never infers a user's activity, chooses a clock time, schedules, authorizes, activates, or starts a conversation.

## Boundaries
M156 does not perform timing selection, scheduling, conversation authorization, prompt generation, response realization, identity/activity/intent inference, behavioral adaptation, provider calls, automation, or platform mutation.

## Consequences
The Living Conversation presence pipeline gains an explicit temporal-evaluation artifact while preserving a clean separation between candidate construction, temporal viability, later timing selection, authorization, realization, and execution across devices and physical contexts.
