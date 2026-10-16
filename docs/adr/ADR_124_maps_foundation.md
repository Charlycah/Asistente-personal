# ADR-124 — Provider-neutral Maps foundation

## Status
Accepted

## Context
ROBY requires a Maps domain that can serve driving, mobile, walking, travel, visual understanding, and ambient context without coupling geospatial concepts to any one runtime or external provider.

## Decision
Introduce `core.maps_foundation` with immutable point signals, governed requests, deterministic map contexts, policy, engine, and repository contracts. The domain validates declared spatial information and eligibility only. It explicitly cannot authorize route computation.

Maps does not depend on Driving. Later orchestration may combine `MapContext` with `DrivingSafetyDecision`, but neither domain owns the other.

## Consequences
- Provider and platform integrations remain replaceable.
- Routing and navigation can evolve independently.
- Consent, precision, confidence, and freshness are explicit from the first Maps milestone.
- M122 cannot fetch, infer, render, or execute geospatial operations.
