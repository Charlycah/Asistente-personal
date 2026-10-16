# M123 — Location Resolution

M123 resolves governed location references from evidence already available to ROBY, without geocoding or provider I/O.

## Responsibilities
- Consume a ready `MapContext` from M122.
- Represent current-location, coordinate, address, place, and region references.
- Select deterministic declared candidates using kind, normalized label, confidence, and ambiguity margin.
- Surface ambiguous, low-confidence, missing-evidence, lineage, and policy failures explicitly.
- Produce immutable, repository-backed `ResolvedLocation` records.

## Architectural position
M123 is downstream from Maps Foundation and upstream from future place knowledge, geocoding adapters, route intent, routing, and navigation.

## Non-responsibilities
M123 does not access GPS, geocoders, map providers, place databases, tiles, traffic, weather, routing engines, navigation systems, cameras, sensors, Android Auto, or CarPlay. It does not search the world for a place and does not compute routes.

## Core invariants
- Only a ready M122 context may be resolved.
- Owner lineage between request and map context must match.
- Current location can only use the point already governed by M122.
- Ambiguous candidates are never guessed.
- Unresolved results expose no selected candidate or point.
- Equal inputs and timestamps produce equal identifiers.
- Repository writes are append-only by identifier.
