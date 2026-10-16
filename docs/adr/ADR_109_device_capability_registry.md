# ADR 109 — Device Capability Registry

## Status
Accepted.

## Decision
Introduce a declarative registry that enriches M106 device capability names with immutable descriptors, state, access, confidence, freshness, version and feature metadata. Compatibility evaluation is conservative and auditable.

## Boundaries
M107 does not execute capabilities, request permissions, discover hardware, transfer context, select an active device or mutate M106 identity. M106 remains the authority for device and session continuity; M107 only answers whether registered capabilities satisfy a stated requirement set.
