# ADR-128 — Navigation Coordination

## Status
Accepted.

## Context
M125 models a governed `RouteIntent` but deliberately does not calculate a route or execute navigation. ROBY needs a stable coordination boundary that decides whether a ready intent may be handed to a future routing capability.

## Decision
Introduce `core.navigation_coordination` as a provider-neutral, side-effect-free domain. It consumes one `RouteIntent` and declarative readiness signals, validates ownership lineage and upstream state, and emits an immutable `NavigationCoordinationDecision`.

The decision may authorize preparation of a future routing request. It never authorizes navigation start or live guidance.

## Invariants
- M126 never calculates distance, duration, geometry, traffic, steps, or instructions.
- M126 never starts navigation or live guidance.
- Upstream incomplete, review, blocked, and not-applicable states propagate conservatively.
- Ownership lineage must match exactly, case-insensitively.
- Explicit authorization and provider/surface availability are policy governed.
- Equal inputs and equal timestamps produce equal identifiers.
- No external I/O or platform mutation occurs.

## Consequences
Future routing and navigation execution layers can consume a stable coordination decision without coupling M126 to providers, Maps SDKs, GPS, traffic, rendering, Driving, or device platforms.
