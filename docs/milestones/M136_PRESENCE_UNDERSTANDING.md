# M136 — Presence Understanding

## Objective
Consolidate anonymous, declarative presence evidence for a governed M135 ambient observation without accessing sensors or identifying people.

## Inputs
- `ResolvedAmbientObservation` from M135 with `PRESENCE_CONTEXT` purpose.
- Zero or more declarative `PresenceEvidence` records.

## Output
- Immutable `PresenceUnderstandingResult`.

## Responsibilities
- Validate owner and exact M135 observation lineage.
- Filter weak, foreign, disallowed, or oversized evidence.
- Resolve duplicate evidence deterministically.
- Detect close conflicts between competing presence states.
- Consolidate one anonymous ambient presence state, attributes, and confidence.
- Persist the result through an abstract repository contract.

## Presence semantics
M136 models only coarse ambient states: unoccupied, occupied, single presence, multiple presences, transient, or unknown. These states are declarative contextual descriptions, not biometric conclusions or precise person counts.

## Explicit exclusions
M136 does not access cameras, microphones, motion sensors, smart-home devices, wearables, vehicle systems, or external providers. It does not identify individuals, perform biometrics, count people precisely, track movement, infer activity, infer relationships, execute automation, or mutate platform state.

## Architectural result
M136 becomes the first interpretation layer of Ambient Context while preserving the strict governed chain M134 → M135 → M136. It supplies anonymous presence context suitable for later ambient integration and Unified Companion consumption without coupling to any device, provider, or execution surface.
