# ADR 218 — Operational Reliability Certification

## Status
Accepted

## Context
M217 produces bounded, traceable stress evidence across the real M211–M216 operational chain. ROBY still lacked a formal authority that evaluates that evidence against explicit reliability criteria and emits an auditable certification result before production-readiness assessment.

## Decision
Introduce `OperationalReliabilityCertifier` as the sole M218 authority for operational reliability certification.

The certifier:

- consumes an identity-matched M217 stress report;
- evaluates minimum bounded coverage;
- rejects failed stress outcomes;
- checks task-failure rate against an explicit threshold;
- verifies that execution was not universally blocked;
- requires complete scenario and report lineage;
- emits immutable `certified`, `conditional`, or `rejected` certificates;
- publishes the effective certification status to the unified cognitive blackboard;
- integrates immediately after M217 in the official runtime composition.

M218 does not run stress scenarios, execute cognitive work, repair failures, mutate infrastructure, approve deployment, or assess production readiness.

## Consequences
ROBY gains a deterministic and auditable reliability gate based on governed M217 evidence. M219 can consume this certificate while retaining exclusive authority over production-readiness assessment.
