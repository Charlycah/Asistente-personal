# ADR 205 — Unified Cognitive Scheduler

## Status
Accepted.

## Context
M201-M204 provide shared signals, global state, event propagation, and cross-domain coordination. ROBY still needs a single governed representation of what cognitive work should occur first, what depends on prior work, and what must remain blocked or advisory.

## Decision
Introduce `UnifiedCognitiveScheduler` as a deterministic, session-scoped, consultative scheduler. It consumes the latest M204 coordination directive and produces an immutable ordered schedule containing domain, action, priority, dependencies, constraints, lineage, and status.

The scheduler:

- preserves owner/session isolation;
- fails closed when M204 is unavailable;
- produces contiguous deterministic sequences;
- maps idle, coordinated, attention-required, and blocked coordination states into explicit schedule states;
- publishes only a governed candidate to M201;
- does not execute contributors, mutate plans, invoke tools, select providers, or arbitrate final authority.

## Consequences
M206 can perform executive arbitration over an explicit schedule rather than over loosely coupled signals. Runtime ordering becomes `M201 -> M202 -> M203 -> M204 -> M205`.
