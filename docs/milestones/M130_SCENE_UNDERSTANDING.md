# M130 — Scene Understanding

## Objective
Consolidate declared scene-level evidence for a governed M129 visual observation without reading or analyzing image pixels.

## Inputs
- `ResolvedVisualObservation` from M129.
- Zero or more declarative `SceneEvidence` records.

## Output
- Immutable `SceneUnderstandingResult`.

## Responsibilities
- Validate owner and observation lineage.
- Filter weak, foreign, disallowed, or oversized evidence.
- Resolve duplicate evidence deterministically.
- Detect close conflicts between competing scene kinds.
- Consolidate a dominant scene, attributes, and confidence.
- Persist the result through an abstract repository contract.

## Non-responsibilities
M130 does not read images, access pixels, call perception models or providers, recognize objects, extract text, identify places or products, perform biometrics, calculate spatial geometry, or mutate platform state.

## Invariants
- Scene understanding is applicable only when M129 explicitly requires it.
- Same governed input and timestamp produce the same identifier.
- An understood result exposes one dominant scene.
- A non-understood result exposes no scene, evidence, attributes, or confidence.
- Object recognition, text extraction, place recognition, biometrics, and pixel access remain disabled.
