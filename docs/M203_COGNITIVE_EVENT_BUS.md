# M203 — Cognitive Event Bus

M203 adds the governed event-distribution layer of ROBY's unified cognitive architecture.

## Purpose

The unified blackboard stores shared cognitive signals and M202 projects a global state. M203 turns relevant state transitions into bounded events so later architecture stages can react without direct module-to-module dependencies.

## Capabilities

- immutable deterministic cognitive events;
- owner/session isolation;
- filtered subscriptions;
- idempotent publication;
- bounded per-session history;
- synchronous delivery records;
- contained consumer failures;
- global-state event publication and blackboard receipt tracing.

## Official runtime order

`M196 → M197 → M198 → M199 → M200 → M201 → M202 → M203 → existing cognitive contributors`

## Governance boundary

M203 transports advisory information only. It does not authorize actions, invoke tools, choose providers, modify memory, rewrite plans, or arbitrate priorities.
