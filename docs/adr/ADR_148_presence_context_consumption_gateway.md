# ADR-148 — Presence Context Consumption Gateway

## Status
Accepted

## Context
M145 materializes governed logical delivery records but intentionally does not expose a stable consumer-facing access boundary. Consumers must not depend directly on publication, subscription, dispatch, or delivery internals.

## Decision
Introduce M146 as a governed consumption gateway downstream from M145. The gateway selects the latest valid logical delivery, validates owner, freshness, confidence, consumer identity, canonical topic, and accepted schema versions, then exposes immutable access records.

Complete and partial deliveries remain explicit. A valid delivery without a compatible item produces an empty result rather than an inferred or transformed payload.

## Boundaries
M146 does not execute consumers, transform context, confirm effective consumption, invoke callbacks, transport messages, infer identity/activity/intent, decide responses, adapt behavior, call providers, automate actions, or mutate the platform.

## Consequences
Consumers receive a stable contract without coupling to internal distribution stages. Future milestones may add specific consumers while preserving the M134–M146 lineage and governance boundaries.
