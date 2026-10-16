# M128 — Visual Understanding Foundation

## Objective
Create ROBY's provider-neutral, governed Visual Understanding domain without performing visual analysis.

## Responsibility
M128 answers: **does a governed visual observation exist for future resolution?**

It validates:
- owner identity;
- explicit visual-context declaration;
- user consent;
- observation source and media type;
- privacy level;
- confidence and freshness;
- external provenance;
- policy limits.

## Output
`VisualContext` with:
- status and action;
- observation availability;
- future observation-resolution requirement;
- external-provider requirement;
- explicit false values for scene understanding, object recognition, text extraction, and biometric analysis;
- rationale and deterministic identifier.

## Non-responsibilities
M128 does not:
- receive, decode, store, or inspect image bytes;
- open cameras, files, streams, screenshots, or video;
- call visual models or external providers;
- perform OCR, captioning, embeddings, classification, detection, segmentation, tracking, face recognition, or biometrics;
- infer scenes, objects, places, identities, colors, depth, or actions;
- integrate with Maps, Driving, Mobile, Ambient Context, or platform state.

## Architectural position
M128 begins a new transversal domain. It is not a child of Mobile or Maps and may later receive governed observations from many devices and contexts.

## Validation target
Ruff clean, focused M128 tests passing, and complete regression suite passing.
