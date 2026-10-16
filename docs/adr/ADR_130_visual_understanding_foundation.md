# ADR-130 — Visual Understanding Foundation

## Status
Accepted.

## Context
ROBY requires a provider-neutral visual domain that can accept governed observation metadata from mobile, desktop, files, screenshots, video frames, and future devices. Coupling the domain directly to cameras, image bytes, models, OCR, object detection, biometrics, or external providers would collapse acquisition, governance, interpretation, and action into one milestone.

## Decision
M128 introduces a declarative Visual Understanding foundation. `VisualUnderstandingFoundationEngine` validates ownership, consent, source, media type, privacy, confidence, freshness, external provenance, and policy limits, then emits an immutable `VisualContext`.

A ready context only states that a governed observation exists and requires future resolution. Scene understanding, object recognition, text extraction, and biometric analysis remain structurally disabled.

## Consequences
- Visual Understanding is independent from Mobile, Driving, Maps, camera adapters, model providers, and platform I/O.
- Future observation-resolution and interpretation milestones receive a stable contract.
- Restricted or externally supplied observations can be blocked by policy before any visual processing occurs.
- M128 cannot read image bytes, call providers, or authorize visual-analysis capabilities.
