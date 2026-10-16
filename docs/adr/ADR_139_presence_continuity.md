# ADR-139 — Presence Continuity

## Status
Accepted

## Context
M136 produces one governed, anonymous, coarse presence interpretation for an M135 ambient observation. ROBY needs temporal coherence between those interpretations, but continuity must not be confused with identity persistence, person tracking, movement reconstruction, or automation.

## Decision
Introduce `core.presence_continuity` as an independent domain downstream from M136.

The domain accepts a bounded sequence of immutable M136 results, validates ownership and exact ambient-context lineage, filters unusable samples, orders them deterministically, applies freshness and gap policy, and emits one immutable continuity result.

The result distinguishes stable continuity, coarse state transition, interruption, review, blocking, and non-applicability. Transition kinds are anonymous contextual labels only: arrival, departure, occupancy change, transient change, and uncertain change.

The domain structurally forbids identity inference, biometric analysis, precise person counting, activity inference, individual tracking, movement tracking, sensor access, and automation.

## Consequences
- Temporal presence coherence has one dedicated responsibility.
- M136 remains a point-in-time interpretation layer.
- No identity or trajectory semantics leak into Ambient Context.
- Freshness, confidence, ordering, deduplication, and temporal gaps are explicit policy concerns.
- Future ambient integration can consume stable continuity without coupling to sensors, providers, or execution surfaces.
