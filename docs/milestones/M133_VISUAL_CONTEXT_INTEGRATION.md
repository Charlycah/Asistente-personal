# M133 — Visual Context Integration

## Objective
Close the Visual Understanding block with one immutable, governed and reusable terminal context.

## Inputs
- `VisualContext` from M128
- optional `ResolvedVisualObservation` from M129
- optional `SceneUnderstandingResult` from M130
- optional `ObjectKnowledgeProfile` from M131
- optional `VisualAttentionPlan` from M132

## Output
`IntegratedVisualContext`

## Responsibilities
- validate exact M128–M132 lineage;
- propagate review and blocked states conservatively;
- preserve available upstream capabilities in partial contexts;
- expose stable identifiers and capability flags;
- remain deterministic, immutable and repository-backed.

## Explicit exclusions
M133 does not read images, inspect pixels, control cameras, detect or track objects, extract text, search products, recognize places, perform biometrics, call providers or mutate platform state.

## Architectural result
Visual Understanding now exposes one terminal contract suitable for Mobile, Driving, Maps, Ambient Context and Unified Companion without exposing internal milestone coupling.
