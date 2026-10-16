# ADR-134 — Visual Attention

## Status
Accepted

## Context
M128–M131 establish governed visual context, observation resolution, scene understanding, and object knowledge. ROBY now needs a stable way to prioritize declared visual entities without introducing pixel analysis, gaze control, cropping, object detection, OCR, product search, place recognition, or biometrics.

## Decision
Introduce M132 as a provider-neutral cognitive attention layer. It consumes the exact M130 scene and M131 object profile plus declarative attention evidence, validates lineage, filters weak or disallowed evidence, resolves duplicates and close conflicts deterministically, and emits an immutable `VisualAttentionPlan`.

## Consequences
Visual consumers receive a stable ordered focus contract. Perception and actuation remain external and prohibited. Future document, product, place, ambient, and unified-companion milestones can consume attention without depending on providers or raw images.
