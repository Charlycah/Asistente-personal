# ADR 107 — Living Conversation Integration

## Status
Accepted — M105

## Context
M93–M104 define a complete set of governed conversational capabilities, from opportunity governance and timing through realization, presence, feedback, rhythm, shared interests, and intellectual curiosity. The stages remain intentionally independent, but Phase X needs one closing boundary that can verify their coherence and expose a single auditable cycle state without collapsing their responsibilities.

## Decision
Introduce `core.living_conversation.integration` as the final Phase X integration boundary.

The integrator receives an M104 `IntellectualCuriosityPlan`, follows its immutable nested references through M103, M102, M101, M100, M99, M98, M96, M95, and M93, validates owner continuity, and produces a `LivingConversationIntegration`.

The result records an integration status, a non-executing next-move recommendation, optional selected curiosity prompt, activation eligibility, user-floor preservation, ordered stage references, rationale, and deterministic identity.

## Boundaries
M105 does not:

- generate or rewrite conversational wording;
- initiate, schedule, deliver, or speak a message;
- select a device, channel, or modality;
- invoke tools or external systems;
- mutate any upstream record;
- write memory, learning, personality, or policy;
- bypass review, rhythm, or user-floor protections.

## Invariants

1. The integration owner matches every owner-bearing stage in the chain.
2. Request and result timestamps are timezone-aware.
3. Stage references are ordered, non-empty, and unique.
4. Only a ready integration may be eligible for activation.
5. Activation eligibility requires a selected M104 prompt.
6. Paused and non-applicable integrations select no prompt.
7. Upstream review propagates conservatively.
8. Closing rhythm, preserved user floor, or disallowed follow-up blocks activation.
9. Same request and timestamp produce the same integration identifier.
10. Repository insertion is append-only and rejects duplicate identifiers.

## Consequences
Phase X closes with one explicit, testable seam that represents the whole living-conversation cycle while preserving every upstream authority and keeping execution outside the phase.
