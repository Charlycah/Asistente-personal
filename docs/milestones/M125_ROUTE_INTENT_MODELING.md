# M125 — Route Intent Modeling

## Objective
Model what movement the user intends without calculating or executing a route.

## Inputs
- resolved origin and destination from M123;
- optional resolved waypoints;
- optional matching place knowledge from M124;
- declared travel mode, priority, constraints, purpose, and time window;
- immutable `RouteIntentPolicy`.

## Output
`RouteIntent`, containing governed endpoint labels, waypoint labels, accepted constraints, rejected evidence count, status, action, clarification/confirmation requirements, future-computation requirement, rationale, timestamp, and deterministic identifier.

## Invariants
- ownership and M123/M124 lineage are preserved;
- unresolved or missing endpoints never produce a ready intent;
- weak endpoints require review;
- conflicting constraints require confirmation;
- duplicate constraints are consolidated deterministically;
- non-ready intents expose no modeled route data;
- ready intent declares future route computation but never performs it;
- no provider, traffic, routing, navigation, rendering, sensor, or platform I/O occurs.

## Architectural sequence
`M122 Maps Foundation -> M123 Location Resolution -> M124 Places Knowledge -> M125 Route Intent Modeling`
