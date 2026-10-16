# M126 — Navigation Coordination

## Objective
Coordinate the transition from a governed M125 `RouteIntent` to a future provider routing request.

## Responsibility
M126 answers: **may this route intent be prepared for routing now?**

It validates:
- owner lineage;
- upstream route-intent status;
- explicit user authorization;
- declared routing-provider availability;
- optional navigation-surface availability;
- policy-controlled background preparation.

## Output
`NavigationCoordinationDecision` with:
- coordination status and action;
- routing-request permission;
- remaining provider, surface, and authorization requirements;
- background-preparation permission;
- immutable lineage to the M125 intent;
- rationale and deterministic identifier.

## Non-responsibilities
M126 does not:
- calculate routes, distance, duration, geometry, or traffic;
- choose paths or optimize routes;
- start navigation;
- issue guidance or instructions;
- access GPS, sensors, providers, Maps SDKs, Android Auto, or CarPlay;
- render maps or mutate platform state.

## Architectural chain
M122 Maps Foundation → M123 Location Resolution → M124 Places Knowledge → M125 Route Intent Modeling → M126 Navigation Coordination.

## Validation target
Ruff clean, focused M126 tests passing, and complete regression suite passing.
