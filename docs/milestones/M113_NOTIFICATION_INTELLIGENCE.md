# M113 — Notification Intelligence

## Objective

Govern whether a mobile notification candidate should surface, defer, suppress, or require confirmation without delivering it.

## Scope

M113 adds:

- structured notification candidates;
- urgency and sensitivity classifications;
- policy-governed relevance thresholds;
- quiet-hours handling with critical exceptions;
- duplicate suppression;
- expiry and freshness checks;
- sensitive-content safeguards;
- interruption scoring;
- conservative propagation of M112 states;
- immutable, deterministic, repository-backed decisions.

## Actions

- `surface`
- `defer`
- `suppress`
- `confirm`
- `none`

## Boundary

M113 does not send, schedule, render, or persist operating-system notifications. It does not request permissions, choose platform APIs, mutate mobile presence, activate audio, or perform network I/O. It only declares notification eligibility and the recommended action.
