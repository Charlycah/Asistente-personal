# M124 — Places Knowledge

## Objective
Establish governed, deterministic knowledge about a location already resolved by M123.

## Inputs
- a successful `ResolvedLocation`;
- declared `PlaceFact` evidence;
- an immutable `PlacesKnowledgePolicy`.

## Output
`PlaceKnowledgeProfile`, containing the resolved place label, accepted facts, rejected evidence count, status, action, provider/confirmation requirements, rationale, timestamp, and deterministic identifier.

## Invariants
- ownership and M123 lineage are preserved;
- unresolved locations are blocked;
- low-confidence and disallowed external facts are rejected;
- close conflicting values require confirmation;
- duplicate evidence is resolved deterministically;
- non-ready profiles expose no facts;
- no search, geocoding, recommendation, routing, navigation, traffic, rendering, or I/O occurs.

## Architectural sequence
`M122 Maps Foundation -> M123 Location Resolution -> M124 Places Knowledge`
