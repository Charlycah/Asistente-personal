# ADR 217 — End-to-End Stress Validation

## Status
Accepted

## Context
M211–M216 established resilience assessment, graceful degradation, recovery coordination, high-load scheduling, long-running stability and bounded concurrent execution. ROBY still lacked a governed way to exercise that complete operational chain repeatedly and produce a traceable stress result before reliability certification.

## Decision
Introduce `EndToEndStressValidator` as the sole M217 authority for bounded synthetic stress validation.

The validator:

- runs explicit demand patterns through the real M211–M216 chain;
- supports nominal, load-sweep, recovery and injected-failure scenarios;
- enforces a hard maximum cycle count;
- records completed, partial, blocked and idle executions;
- counts isolated task failures and peak worker use;
- preserves source lineage across every cycle;
- emits deterministic `passed`, `degraded` or `failed` reports;
- publishes a bounded runtime probe to the unified cognitive blackboard.

M217 does not benchmark external providers, mutate infrastructure, scale clusters, restart services, certify operational reliability or assess production readiness.

## Consequences
ROBY gains reproducible end-to-end stress evidence over its unified hardening chain. M218 can use this governed evidence for operational reliability certification without redefining execution or recovery authority.
