# ADR-129 — Map Context Integration

## Status
Accepted.

## Context
M122–M126 establish provider-neutral geospatial context, governed location resolution, place knowledge, route intent, and navigation coordination. Consumers such as Mobile, Driving, Visual, Ambient Context, and Unified Companion should not depend on every internal Maps contract separately.

## Decision
Introduce `core.map_context_integration` as the terminal, side-effect-free integration boundary of the Maps domain. It validates owner and identifier lineage across supplied M122–M126 outputs and emits one immutable `IntegratedMapContext`.

The integrated context summarizes available spatial context, place knowledge, route intent, and permission to prepare a provider routing request. It preserves partial and review-required upstream states conservatively.

## Invariants
- M127 never recalculates M122–M126 decisions.
- Every supplied location must belong to the supplied M122 `MapContext`.
- Every supplied place profile must belong to an included M123 location.
- Every supplied route endpoint and waypoint must belong to an included M123 location.
- Every supplied M126 decision must reference the supplied M125 intent.
- M127 never calculates distance, duration, traffic, geometry, steps, or instructions.
- M127 never starts navigation or authorizes live guidance.
- Equal inputs and equal timestamps produce equal identifiers.
- No external I/O or platform mutation occurs.

## Consequences
Future ROBY domains can consume one stable Maps integration contract without coupling themselves to the internal M122–M126 pipeline or to providers, GPS, Maps SDKs, rendering, routing engines, or device platforms.
