# ADR-127 — Route Intent Modeling

## Status
Accepted

## Context
M122 established provider-neutral map context, M123 resolved location identity, and M124 established governed place knowledge. ROBY now needs a stable representation of intended movement before any route provider, routing algorithm, traffic source, or navigation runtime is introduced.

## Decision
Create `core.route_intent_modeling` as a pure governed domain. It consumes resolved origin, destination, optional waypoints, optional matching place-knowledge profiles, declared travel mode, priority, constraints, purpose, and time window. It validates ownership and lineage, rejects unresolved or weak endpoints, consolidates constraints deterministically, and emits an immutable `RouteIntent`.

## Boundaries
M125 does not geocode, search, calculate distance or duration, optimize routes, query traffic, choose roads, render maps, navigate, access GPS, call providers, or mutate platforms. A ready intent only declares that future route computation is required.

## Consequences
Route intent remains reusable across driving, walking, cycling, transit, mixed travel, mobile, and future unified-companion contexts. Routing and navigation can evolve independently behind a stable declarative contract.
