# M132 — Visual Attention

## Objective
Prioritize governed visual entities from an M130 scene and M131 object profile without reading pixels or controlling a camera, crop, viewport, or gaze.

## Inputs
- `SceneUnderstandingResult` from M130.
- `ObjectKnowledgeProfile` from M131.
- Zero or more declarative `VisualAttentionEvidence` records.

## Output
- Immutable `VisualAttentionPlan`.

## Responsibilities
- Validate owner and exact M130→M131 lineage.
- Accept attention only for objects already present in M131.
- Filter weak, foreign, external, oversized, or stale-by-contract evidence.
- Resolve duplicate evidence deterministically.
- Consolidate reasons and rank focus items by governed priority.
- Require review for close conflicting priorities.
- Persist plans through an abstract repository contract.

## Non-responsibilities
M132 does not read images, access pixels, detect or track objects, crop images, control gaze or camera direction, extract text, search products, identify places, perform biometrics, call perception providers, or mutate platform state.

## Invariants
- Attention requires an understood M130 scene and available M131 object knowledge.
- Every focus item must reference an existing M131 object.
- Same governed input and timestamp produce the same identifier.
- Available attention exposes at least one immutable focus item.
- Inactive output exposes no focus items or confidence.
- Perceptive and actuation capabilities remain disabled.
