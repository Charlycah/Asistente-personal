# M131 — Object Knowledge

## Objective
Consolidate declared object-level evidence for a governed M130 scene without reading pixels or detecting visual objects.

## Inputs
- `SceneUnderstandingResult` from M130.
- Zero or more declarative `ObjectEvidence` records.

## Output
- Immutable `ObjectKnowledgeProfile`.

## Responsibilities
- Validate owner, scene, and observation lineage.
- Filter weak, foreign, disallowed, or oversized evidence.
- Resolve duplicate evidence deterministically.
- Consolidate logical objects by stable object reference.
- Preserve category, label, attributes, count, confidence, and evidence references.
- Detect close semantic conflicts and require review.
- Persist profiles through an abstract repository contract.

## Non-responsibilities
M131 does not read images, access pixels, detect or track objects, extract text, search products, identify places, perform biometrics, call perception models or providers, or mutate platform state.

## Invariants
- Object knowledge requires an understood M130 scene.
- Evidence must belong to the exact resolved observation lineage.
- Same governed input and timestamp produce the same identifier.
- Available knowledge exposes at least one immutable object.
- Inactive output exposes no objects or confidence.
- Detection, tracking, OCR, product search, place recognition, biometrics, and pixel access remain disabled.
