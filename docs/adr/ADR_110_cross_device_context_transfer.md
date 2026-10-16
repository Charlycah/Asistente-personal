# ADR-110 — Cross-Device Context Transfer

## Status
Accepted.

## Context
M106 establishes device identity and session continuity. M107 describes and evaluates device capabilities. A separate boundary is required to decide which session context may be prepared for transfer without performing transport or mutating any source state.

## Decision
Introduce `core.context_transfer` as a deterministic, immutable and auditable manifest layer.

The layer accepts:

- an M106 continuity decision;
- an M107 capability match;
- explicit context fragment descriptors containing references, revisions, digests, sensitivity and capability requirements.

It produces a transfer manifest with included, excluded and review-required fragment identifiers, the M106 resume cursor, a deterministic manifest digest, status, action and rationale.

## Invariants

- Ownership and session identity must agree across the complete chain.
- The M107 match must describe the M106 target device.
- Only M106 `ready` decisions may proceed.
- Required capability evaluation is conservative.
- Restricted, sensitive, expired and capability-incompatible context is governed explicitly.
- Raw context payloads, credentials and secrets are not stored in the manifest.
- No source object is mutated.
- The layer does not transmit, synchronize or activate a device.

## Consequences
M108 creates a stable contract for future transport and active-device arbitration while preserving separation from networking, persistence, memory and user-interface concerns.
