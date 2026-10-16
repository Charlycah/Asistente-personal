# ADR-132 — Scene Understanding

## Status
Accepted.

## Context
M129 resolves which governed visual representation should continue through the visual pipeline, but deliberately does not interpret its contents. ROBY needs a provider-neutral boundary for scene-level understanding that does not couple the domain to image bytes, cameras, perception models, or external providers.

## Decision
Introduce `core.scene_understanding`. M130 consumes a resolved M129 observation and declarative scene evidence produced by future perception adapters. It validates owner and observation lineage, confidence, provenance, collection limits, duplicate references, and ambiguity before emitting an immutable `SceneUnderstandingResult`.

M130 may consolidate a dominant scene kind and normalized scene attributes. It cannot inspect pixels or authorize object recognition, OCR, place recognition, product understanding, biometrics, provider calls, or platform mutation.

## Consequences
- Scene semantics become stable and provider-neutral.
- M129 remains the authority for representation selection and visual lineage.
- Future object, text, product, and place milestones can consume scene context without duplicating scene consolidation.
- Actual perception and image I/O remain outside the domain layer.
