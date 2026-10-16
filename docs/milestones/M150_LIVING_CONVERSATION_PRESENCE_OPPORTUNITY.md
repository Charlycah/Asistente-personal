# M150 — Living Conversation Presence Opportunity

## Responsibility
Convert governed M149 presence policy into a declarative potential conversational opportunity.

## Inputs
Immutable `LivingConversationPresencePolicyResult` values from M149.

## Outputs
Immutable opportunity results classified as available, available with partial context, inhibited, review required, blocked, or not applicable.

## Guarantees
- Exact M149 source preservation.
- Deterministic selection, deduplication and identifiers.
- Owner, age, confidence, partial-context and result-limit governance.
- No conversation decision, activation, timing, prompt generation, response realization, inference, automation or mutation.
