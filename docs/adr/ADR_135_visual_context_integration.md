# ADR-135 — Visual Context Integration

## Status
Accepted.

## Context
M128–M132 establish governed visual context, resolve the observation, consolidate scene semantics, consolidate object knowledge and prioritize visual attention. Consumers outside the visual domain need one stable terminal contract without depending on every internal milestone.

## Decision
Introduce `core.visual_context_integration` as the terminal integration boundary for the visual domain. It validates owner and lineage continuity across M128–M132, preserves partial and review-required states conservatively, and emits an immutable `IntegratedVisualContext`.

The integration layer does not recalculate upstream results and does not authorize perception or actuation. Pixel access, camera control, detection, tracking, OCR, product search, place recognition and biometric analysis remain structurally disabled.

## Consequences
- Mobile, Driving, Maps, Ambient Context and Unified Companion can consume one stable visual contract.
- Upstream visual milestones remain independently testable and replaceable.
- Partial visual knowledge can be retained without inventing missing stages.
- Provider adapters and perceptive runtimes remain outside the cognitive integration boundary.
