# ADR 202 — Global Cognitive State

## Decision

ROBY will add a deterministic global cognitive state projection immediately after M201. M202 reads the current owner/session blackboard snapshot, aggregates the visible domains and signal quality, derives a bounded readiness state, and publishes that projection back to the unified cognitive blackboard.

## State model

The global cognitive readiness is one of:

- `stable`: current cognitive signals are available and no active constraint limits the turn.
- `limited`: the system can continue, but grounding, expectation calibration, or an explicit constraint must remain visible.
- `blocked`: conversational repair is required before reliable continuation.
- `degraded`: the blackboard does not yet contain enough governed signals for a reliable global projection.

The projection also includes active domains, signal count, average confidence, explicit constraints, dimensions, and exact source lineage.

## Constraints

- M202 is derived exclusively from a session-scoped M201 snapshot.
- The projection is deterministic for the same snapshot and timestamp.
- Source entries remain authoritative and are never rewritten.
- Previous `global_cognitive_state` publications are excluded from the next aggregation to prevent self-amplification.
- State remains isolated by owner and session.
- M202 publishes advisory context only.
- M202 cannot execute tools, select providers, mutate memory, rewrite plans, arbitrate priorities, bypass governance, or create commitments.
- Official contributor order is M196, M197, M198, M199, M200, M201, M202, then existing cognitive stages.
- M202 requires the official unified cognitive blackboard.

## Consequences

M203-M210 receive one stable global state surface for events, cross-domain coordination, scheduling, executive arbitration, context fusion, health monitoring, optimization, and whole-system integration. The operational runtime remains authoritative and unchanged.
