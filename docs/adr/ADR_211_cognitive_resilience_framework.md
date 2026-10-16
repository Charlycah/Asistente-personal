# ADR 211 — Cognitive Resilience Framework

## Status

Accepted.

## Context

M210 exposes a deterministic whole-system readiness report, but operational hardening requires an explicit interpretation of how the unified cognitive architecture should preserve safe behavior when components become constrained, degraded, or blocked. This interpretation must remain separate from actual degradation and recovery execution, which belong to M212 and M213.

## Decision

Introduce `CognitiveResilienceFramework` after M210 in the official cognitive runtime. It derives:

- a resilience posture: robust, guarded, degraded, or contained;
- explicit cognitive failure domains;
- deterministic, priority-ordered safeguards;
- a bounded resilience score and complete source lineage.

The framework publishes its posture to the unified cognitive blackboard and contributes governed runtime context. It does not execute fallbacks, change schedules, recover components, invoke tools, route providers, or mutate runtime configuration.

## Consequences

- M211 creates a stable resilience contract for M212 and M213.
- Failure interpretation becomes deterministic, traceable, and owner/session scoped.
- Existing execution and governance boundaries remain unchanged.
- Graceful degradation and coordinated recovery remain intentionally unavailable until their dedicated milestones.
