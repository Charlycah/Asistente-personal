# ADR-121 — Driving Interaction Policy

## Status
Accepted

## Context
M118 exposes driving contextual load and basic interaction suitability, but future driving conversation layers require a dedicated decision boundary for urgency, direction, deferrability, interruption, acknowledgement, and response limits. Embedding those rules in conversation realization would couple safety policy to content generation and delivery.

## Decision
Introduce `core.driving_interaction_policy` as an immutable policy layer over M118. It accepts a declarative interaction signal and produces a governed envelope describing listening, response, proactivity, interruption, acknowledgement, deferral, and maximum response duration.

## Invariants
- M117 owns eligibility; M118 owns contextual load; M119 owns interaction policy only.
- Critical contexts conservatively defer ordinary interaction.
- Emergency behavior is explicit and policy-controlled.
- Non-ready outcomes expose no interaction permission.
- The domain performs no content generation, modality execution, navigation, sensor, or platform I/O.
- Outputs are deterministic, immutable, auditable, and repository-backed.

## Consequences
Future conversation adaptation can remain focused on realization while consuming a stable safety envelope. Navigation, maps, visual, ambient, and unified-companion domains remain decoupled from driving policy internals and hardware acquisition.
