# ADR-138 — Presence Understanding

## Status
Accepted

## Context
M134 establishes governed Ambient Context and M135 resolves a purpose-specific declarative observation representation. Presence interpretation must begin without collapsing governance, sensing, identity, tracking, activity, and automation into one component.

## Decision
Introduce `core.presence_understanding` as an independent domain downstream from M135.

The domain accepts only a resolved `PRESENCE_CONTEXT` observation and declarative anonymous presence evidence. It validates ownership and exact observation lineage, applies confidence and provenance policy, resolves duplicates deterministically, detects ambiguity, and emits one immutable coarse presence state.

The domain structurally forbids identity inference, biometric analysis, precise person counting, activity inference, movement tracking, sensor access, and automation.

## Consequences
- Ambient interpretation begins incrementally without provider or sensor coupling.
- Presence remains anonymous, coarse, and context-oriented.
- Future activity, acoustic, environmental, spatial, and integration milestones can depend on a stable governed contract.
- Device-specific sensing and execution remain outside the domain.
