# ADR 207 — Global Context Fusion

## Status
Accepted.

## Context
M201–M206 provide a blackboard, global state, event propagation, coordination,
scheduling, and executive arbitration. Downstream cognition still needs one
coherent, traceable view of those sources without direct coupling.

## Decision
Introduce `GlobalContextFusionEngine` after M206. It projects blackboard facts,
global state constraints, cognitive events, and executive task dispositions
into an immutable `GlobalContextView` scoped to owner and session.

The projection preserves conflicts and constraints, excludes its own prior
publication from aggregation, and publishes only a governed context receipt to
M201. It cannot execute tools, mutate memory, alter plans, select providers, or
replace source records.

## Consequences
M208–M210 can consume one stable context contract while retaining exact source
lineage and existing governance boundaries.
