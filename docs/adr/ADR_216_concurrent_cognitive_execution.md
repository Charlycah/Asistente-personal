# ADR 216 — Concurrent Cognitive Execution

## Status
Accepted

## Context
M214 governs admission under load and M215 evaluates long-running stability, but ROBY still lacked an execution authority able to run independent admitted cognitive work in parallel. M216 must add real concurrency without surrendering deterministic outputs, failure isolation, bounded resource use, or the safety constraints emitted by M215.

## Decision
Introduce `ConcurrentCognitiveExecutor` as the sole M216 authority for bounded concurrent cognitive execution.

The executor:

- consumes the latest M215 stability assessment and M214 high-load schedule;
- executes only admitted actions for which an explicit handler exists;
- uses a bounded `ThreadPoolExecutor`;
- captures task failures as typed results instead of propagating them across siblings;
- restores logical sequence order after nondeterministic completion;
- blocks execution while M215 is `guarded`;
- reduces execution to one worker while a checkpoint is required;
- publishes the effective execution status to the unified cognitive blackboard.

M216 does not restart providers, scale infrastructure, mutate platform state, or perform end-to-end stress certification.

## Consequences
ROBY gains real parallel cognitive execution while preserving deterministic integration and explicit operational boundaries. M217 may now validate the complete chain under stress without redefining execution authority.
