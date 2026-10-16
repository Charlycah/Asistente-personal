# M127 — Map Context Integration

## Objective
Close the provider-neutral Maps block with one governed integration contract over M122–M126.

## Responsibility
M127 answers: **what governed map context is currently available to downstream ROBY domains?**

It validates:
- owner lineage;
- M122 map-context readiness;
- M123 location ownership and map-context lineage;
- M124 place-profile ownership and location lineage;
- M125 route endpoint and waypoint lineage;
- M126 navigation-decision lineage;
- collection limits and partial/review states.

## Output
`IntegratedMapContext` with:
- terminal status and action;
- immutable identifiers for all accepted upstream records;
- spatial-context, place-knowledge, and route-intent availability;
- routing-preparation permission inherited from M126;
- explicit confirmation requirement;
- rationale and deterministic identifier.

## Non-responsibilities
M127 does not:
- resolve locations or consolidate place facts;
- model route intent or coordinate providers;
- calculate distance, duration, traffic, geometry, or routes;
- issue steps or navigation instructions;
- start navigation or live guidance;
- access GPS, sensors, providers, Maps SDKs, Android Auto, or CarPlay;
- render maps or mutate platform state.

## Architectural chain
M122 Maps Foundation → M123 Location Resolution → M124 Places Knowledge → M125 Route Intent Modeling → M126 Navigation Coordination → M127 Map Context Integration.

## Validation target
Ruff clean, focused M127 tests passing, and complete regression suite passing.
