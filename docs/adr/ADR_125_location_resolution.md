# ADR-125 — Location Resolution

## Status
Accepted.

## Context
M122 establishes a governed, provider-neutral geospatial context but intentionally does not resolve human references such as “here”, an address label, a place name, or a declared coordinate candidate. ROBY needs a stable resolution contract before place knowledge, geocoding providers, routing, or navigation can be introduced.

## Decision
Introduce `core.location_resolution` as a separate domain that consumes a ready `MapContext` and declarative location evidence. It produces an immutable `ResolvedLocation` with explicit resolved, ambiguous, review-required, blocked, or not-applicable outcomes.

Resolution is deterministic and conservative. Current-location references may use the point already governed by M122. Other references may select only from supplied candidates. Exact normalized label matches are preferred; otherwise candidates are ranked by confidence and ambiguity margin. No provider call is performed.

## Consequences
- M123 establishes a stable boundary for future geocoders and place catalogs.
- Provider selection, external search, place semantics, routing, navigation, traffic, rendering, and sensor access remain outside this milestone.
- Maps remains transversal and does not depend on Driving.
- Ambiguous evidence is surfaced rather than guessed.
