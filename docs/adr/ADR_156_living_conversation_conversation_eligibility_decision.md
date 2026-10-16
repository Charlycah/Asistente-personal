# ADR-156 — Living Conversation Conversation Eligibility Decision

## Status
Accepted

## Context
M153 declares whether a selected presence opportunity is ready, partially ready, or not ready. The architecture still requires a separate governed boundary that decides whether readiness is eligible to advance toward later conversational decision stages without starting a conversation or selecting timing.

## Decision
Add M154 as a pure eligibility-decision layer downstream from M153.

M154:

- consumes immutable M153 readiness results;
- selects the best valid readiness result deterministically;
- declares `ELIGIBLE`, `ELIGIBLE_PARTIAL`, or `NOT_ELIGIBLE`;
- preserves the exact M153 readiness and M150 opportunity objects;
- applies owner, freshness, confidence, partial-context, deduplication, and result-limit governance;
- never starts or activates a conversation.

## Boundaries
M154 does not select timing, generate prompts, realize responses, infer identity/activity/intent, adapt behavior, call providers, automate actions, or mutate the platform.

## Consequences
The Living Conversation presence pipeline gains an explicit governed eligibility boundary while preserving the separation between readiness, eligibility, timing, realization, and execution.
