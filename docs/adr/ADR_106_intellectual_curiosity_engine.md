# ADR 106 — Intellectual Curiosity Engine

## Status
Accepted — M104

## Context
M103 identifies shared intellectual interests from explicit, traceable conversational evidence. ROBY still needs a governed way to derive possible directions for inquiry without turning an inferred interest into memory, initiating a conversation, choosing timing, or generating final conversational wording.

## Decision
Introduce `core.living_conversation.curiosity` as a channel-neutral planning layer after M103.

The engine accepts a `SharedIntellectualInterestsAssessment` and produces an immutable `IntellectualCuriosityPlan` containing ranked proposals of five kinds: question, connection, counterpoint, exploration, and revisit.

Every proposal preserves source references and carries a bounded score. The engine supports topic exclusions, requested proposal kinds, configurable limits, conservative review propagation, deterministic identifiers, and an explicit rationale when conversational rhythm discourages immediate activation.

## Boundaries
M104 does not:

- initiate or deliver conversation;
- select timing, channel, device, or modality;
- rewrite M99 realization content;
- modify M100 presence or M102 rhythm;
- persist interests as personal memory;
- update learning, personality, or policy;
- invoke tools or external systems.

## Invariants

1. Owner identity must match the M103 assessment owner.
2. Input and output timestamps are timezone-aware.
3. Non-actionable plans contain no prompts.
4. Prompts are unique by normalized topic and curiosity kind.
5. Every prompt contains at least one source reference.
6. Scores remain within `[0, 1]`.
7. Review state propagates conservatively from M103.
8. Same input and timestamp produce the same plan identifier.
9. Repository insertion is append-only and rejects duplicate identifiers.

## Consequences
Curiosity becomes explicit, auditable, testable, and reusable by later conversational orchestration without coupling intellectual exploration to activation or memory.
