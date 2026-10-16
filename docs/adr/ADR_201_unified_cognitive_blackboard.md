# ADR 201 — Unified Cognitive Blackboard

## Decision

ROBY will add a governed, append-only cognitive blackboard immediately after M200. The blackboard provides a shared exchange surface where cognitive domains can publish immutable, traceable signals and obtain session-scoped snapshots without depending directly on one another.

## Constraints

- Entries are immutable value objects with deterministic identifiers.
- State is isolated by owner and session.
- Retention is bounded independently for each session.
- Duplicate publication of the same entry is idempotent.
- Reads may be filtered by cognitive domain.
- M201 initially publishes the M200 operational conversation state as the first governed blackboard signal.
- Blackboard data is advisory context only; publication does not authorize execution.
- M201 cannot execute tools, select providers, mutate memory, rewrite plans, bypass governance, or create autonomous commitments.
- Official contributor order is M196, M197, M198, M199, M200, M201, then existing cognitive stages.
- Failures remain contained by the official cognitive runtime orchestrator.

## Consequences

M202-M210 gain one stable cross-domain coordination surface. Future cognitive state, event, scheduling, arbitration, context fusion, health, and optimization capabilities can publish and consume governed signals without introducing direct module coupling. The operational runtime remains authoritative and unchanged.
