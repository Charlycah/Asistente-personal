# M102 — Conversational Rhythm Regulation

## Objective
Regulate the cadence of a living conversation after M101 feedback while preserving the user's conversational floor and avoiding delivery concerns.

## Scope
M102 introduces:

- brisk, steady, measured, paused, and closing rhythms;
- regulated, review-required, and not-applicable statuses;
- governed advisory intervals;
- maximum consecutive ROBY-turn limits;
- follow-up prompt permission;
- user-floor preservation;
- interruption, silence, long-response, and observed-cadence inputs;
- immutable repository-backed decisions;
- deterministic identities and complete rationale.

## Architectural boundary
M102 consumes M101 feedback and local exchange observations. It does not rewrite M99, alter M100 or M101, wait, schedule, deliver messages, invoke tools, modify memory, update personality, or learn automatically.

## Verification
- 33 focused M102 tests.
- Full Ruff validation.
- Full pytest regression suite.
