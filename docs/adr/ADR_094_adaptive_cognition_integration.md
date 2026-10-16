# ADR-094 — Adaptive Cognition Integration

## Status

Accepted for M92.

## Context

M85–M91 introduced separate governed faculties for episodes, mental models,
meta-reasoning, reflection, knowledge evolution, executive planning and
executive coordination. Their individual boundaries are correct, but the safe
automatic path after M84 remained embedded directly in `CognitivePipeline`.

## Decision

Introduce `AdaptiveCognitionManager` as the Phase IX integration boundary. It
records an immutable `AdaptiveCognitionCycle` with one stage record per Phase IX
faculty.

The manager may automatically:

1. capture an M84 result as an M85 episode;
2. evaluate it through M87;
3. produce an advisory M88 reflection.

M86 is exposed as contextual capability. M89, M90 and M91 are reported as
available but are never invoked automatically because each requires explicit
candidate content, objectives, directives or governance decisions.

When configured in `CognitivePipeline`, the manager replaces the legacy direct
M85/M87/M88 chaining and prevents duplicate processing. Existing installations
without M92 preserve the previous behavior.

## Invariants

- Experience is not evidence or knowledge.
- Assessment does not replace the evaluated conclusion.
- Reflection remains advisory.
- Knowledge evolution, planning and coordination require explicit invocation.
- Integration never executes tools, creates tasks or grants permissions.
- Every cycle is immutable, timestamped and traceable to an M84 result.
- Stage references are unique and stage identities cannot repeat in one cycle.
- Review requirements propagate to the integrated cycle.

## Consequences

Phase IX gains one public integration surface without collapsing the internal
faculties. Consumers can inspect readiness, audit completed stages and continue
to invoke governed evolution or executive components explicitly.
