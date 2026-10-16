# M101 — Conversational Feedback Loop

## Objective
Assess post-presence conversational signals and produce governed, auditable recommendations for the next conversational move.

## Scope
M101 introduces:

- explicit, implicit, and system feedback origins;
- acceptance, correction, confusion, rejection, deepening, disengagement, and no-signal kinds;
- assessed, insufficient, review-required, and not-applicable statuses;
- advisory adjustments for maintaining, clarifying, correcting, deepening, reducing intensity, closing follow-up, or seeking confirmation;
- confidence governance and implicit-signal caps;
- immutable repository-backed assessments;
- deterministic identities and complete rationale.

## Architectural boundary
M101 observes and assesses what follows M100. It does not rewrite M99, alter M100, send messages, invoke tools, modify memory, update personality, or perform automatic learning.

## Verification
- 32 focused M101 tests.
- Full Ruff validation.
- Full pytest regression suite.
