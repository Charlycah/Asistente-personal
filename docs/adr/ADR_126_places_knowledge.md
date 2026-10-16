# ADR-126 — Places Knowledge

## Status
Accepted

## Context
M122 established provider-neutral map context and M123 resolved declared location references. ROBY now needs a bounded representation of what is known about a resolved place without introducing provider lookup, search, recommendations, routing, navigation, or side effects.

## Decision
Create `core.places_knowledge` as a pure governed domain. It consumes one successful `ResolvedLocation` and declared `PlaceFact` evidence. It validates ownership and lineage, filters low-confidence or disallowed external evidence, resolves duplicate facts deterministically, detects close conflicts, and emits an immutable `PlaceKnowledgeProfile`.

## Boundaries
M124 performs no geocoding, provider I/O, places search, distance calculation, recommendation, routing, navigation, traffic evaluation, rendering, or platform mutation. Future adapters may supply facts, but they cannot bypass M124 governance.

## Consequences
Places knowledge remains reusable across mobile, driving, walking, travel, visual, and ambient contexts. M123 remains the authority for location identity, while later milestones can consume a stable knowledge profile without depending on providers.
