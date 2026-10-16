# M134 — Ambient Context Foundation

## Objective
Open Ambient Context as an independent, provider-neutral and governed domain.

## Input
`AmbientContextFoundationRequest` containing an optional declarative `AmbientObservationSignal`.

## Output
`AmbientContext`.

## Responsibilities
- validate ownership and explicit consent;
- govern observation source, scope and privacy;
- validate confidence, freshness and external provenance;
- expose deterministic immutable context identity;
- declare whether future ambient resolution is required.

## Explicit exclusions
M134 does not read sensors, microphones, cameras, weather services, smart-home systems or platform state. It does not infer people, presence, activities, rooms, sound, climate, hazards or spatial relations, and it never executes automation.

## Architectural result
Ambient Context becomes a transversal domain suitable for future consumption by Mobile, Driving, Maps, Visual Understanding and Unified Companion without depending on any of them.
