# M129 — Visual Observation Resolution

## Objective
Resolve which declared representation of a governed M128 observation should continue through the visual pipeline.

## Inputs
- `VisualContext` from M128.
- Requested visual purpose.
- Optional declarative representation candidates.

## Output
- Immutable `ResolvedVisualObservation`.

## Responsibilities
- Validate owner and observation lineage.
- Filter weak, disallowed, malformed, or foreign candidates.
- Select a representation deterministically.
- Preserve purpose and future-capability requirements.
- Persist the resolution through an abstract repository contract.

## Non-responsibilities
M129 does not read images, inspect pixels, access cameras or files, call providers, infer scenes, recognize objects, extract text, identify products or places, perform biometrics, or mutate platform state.

## Invariants
- Same governed input and timestamp produce the same identifier.
- A resolved result has exactly one selected candidate.
- A non-resolved result exposes no selected candidate.
- Candidate lineage must match the M128 observation reference.
- Pixel access and biometric analysis are always disabled.
