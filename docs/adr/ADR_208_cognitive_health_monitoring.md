# ADR 208 — Cognitive Health Monitoring

## Status
Accepted.

## Context
M201–M207 provide a shared blackboard, global state, event propagation, cross-domain coordination, scheduling, executive arbitration, and fused global context. The integrated architecture now requires a governed way to observe its health without allowing monitoring to mutate cognition or execute recovery actions.

## Decision
Introduce `CognitiveHealthMonitor` as a deterministic, owner/session-scoped observer over M207. It produces immutable reports with health dimensions, aggregate score, alerts, source lineage, and one of four states: `healthy`, `watch`, `degraded`, or `critical`.

The monitor assesses context coverage, signal confidence, coherence, constraints, deferred work, and cognitive availability. It publishes only a governed health receipt to M201.

## Boundaries
M208 does not execute tools, repair conflicts, alter schedules, override arbitration, modify memory, select providers, or authorize actions. Corrective and optimization behavior remains outside its authority.

## Consequences
M209 can consume stable health reports to recommend performance improvements, while M210 can validate whole-system readiness using explicit diagnostic evidence.
