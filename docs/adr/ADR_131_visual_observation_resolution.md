# ADR-131 — Visual Observation Resolution

## Status
Accepted.

## Context
M128 establishes a governed visual observation but deliberately performs no image I/O or visual analysis. The next layer needs a provider-neutral way to choose which declared representation of that observation should continue through the visual pipeline.

## Decision
Introduce `core.visual_observation_resolution`. M129 consumes a ready `VisualContext` and zero or more declarative representation candidates. It validates owner and observation lineage, confidence, provenance, limits, and requested purpose, then emits an immutable `ResolvedVisualObservation`.

The selected representation may be the original observation, a preview, a document page, a video keyframe, or a screen region. Selection is deterministic and does not inspect pixels.

M129 may declare which future understanding capability is required, but it cannot authorize or execute scene understanding, object understanding, text extraction, product search, place recognition, pixel access, biometrics, provider calls, or platform mutation.

## Consequences
- Visual representation selection is stable and provider-neutral.
- M128 remains the authority for consent, privacy, freshness, and provenance.
- Future understanding milestones receive a single governed representation.
- Image analysis remains outside M129.
