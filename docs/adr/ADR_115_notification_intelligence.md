# ADR-115 — Notification Intelligence

## Status

Accepted.

## Context

M112 governs the logical lifecycle of ROBY's mobile presence, but ROBY still needs a governed way to decide whether a mobile notification candidate deserves interruption, deferral, suppression, or human confirmation. Delivery through an operating-system API remains outside this decision layer.

## Decision

Introduce `core.notification_intelligence` as an immutable, deterministic, repository-backed decision layer over M112.

The engine evaluates:

- M112 presence status and next state;
- candidate relevance, urgency, sensitivity, age, and expiry;
- quiet hours and critical exceptions;
- user presence and device lock state;
- network availability;
- deduplication keys;
- acknowledgement requirements;
- policy-governed interruption cost.

It produces one of `surface`, `defer`, `suppress`, `confirm`, or `none` with an interruption score and rationale.

## Boundaries

M113 does not deliver notifications, call operating-system APIs, render content, select a transport, schedule retries, request permissions, activate sensors, or mutate M112. It only evaluates a notification candidate.

## Consequences

Notification decisions become auditable and portable across future mobile platforms while preserving a strict distinction between decision and execution.
