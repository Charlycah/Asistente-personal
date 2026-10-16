# M122 — Maps Foundation

M122 opens the Maps domain as a governed, provider-neutral geospatial foundation.

## Responsibilities
- Represent declared geographic points with validated coordinates, confidence, source, and observation time.
- Govern maps eligibility through purpose, requested precision, requested scope, consent, confidence, and freshness.
- Produce immutable, deterministic `MapContext` records.
- Expose whether location context is available and whether a future provider integration is required.
- Preserve a domain boundary reusable from mobile, driving, walking, travel, visual, and ambient contexts.

## Architectural position
M122 is not a child of Driving. It is a transversal domain. Driving may consume future Maps contracts, but Maps does not depend on M117–M121.

## Non-responsibilities
M122 does not access GPS, geocoders, map tiles, place databases, traffic services, weather, routing engines, navigation systems, cameras, sensors, Android Auto, or CarPlay. It does not compute routes, resolve addresses, search places, render maps, or mutate device location settings.

## Core invariants
- Coordinates are validated before context establishment.
- Non-ready contexts expose no location capability.
- Route computation is always false in M122.
- Equal inputs and timestamps produce equal identifiers.
- Repository writes are append-only by identifier.

## Future compatibility
The foundation intentionally leaves provider selection, geocoding, place understanding, routing, navigation guidance, traffic awareness, visual grounding, and ambient fusion to later milestones.
