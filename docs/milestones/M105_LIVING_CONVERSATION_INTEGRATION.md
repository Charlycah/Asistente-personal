# M105 — Living Conversation Integration

## Objective
Close Phase X by integrating M93–M104 into one coherent, immutable, auditable cycle result without creating a delivery or execution layer.

## Architecture
M105 consumes the M104 curiosity plan because that object already preserves the complete nested upstream chain. It validates owner continuity, extracts ordered identifiers for the ten upstream stages, and evaluates whether the cycle is ready, requires review, must pause, or is not applicable.

## Public contracts

- `LivingConversationIntegrationStatus`
- `LivingConversationNextMove`
- `LivingConversationIntegrationPolicy`
- `LivingConversationIntegrationRequest`
- `LivingConversationIntegration`
- `LivingConversationIntegrationRepository`
- `InMemoryLivingConversationIntegrationRepository`
- `LivingConversationIntegrator`

## Outcomes

- `ready / explore`: a curiosity prompt is eligible for a later activation layer;
- `review_required / clarify`: an upstream ambiguity blocks automatic progress;
- `paused / wait`: rhythm or user-floor protections require restraint;
- `paused / close`: the conversational cycle should close;
- `not_applicable / none`: the upstream chain cannot support a conversation.

## Integration references
The output preserves ordered identifiers for:

1. M93 governance;
2. M95 timing;
3. M96 reflection;
4. M98 intellectual contribution;
5. M99 realization;
6. M100 presence;
7. M101 feedback;
8. M102 rhythm;
9. M103 shared interests;
10. M104 curiosity.

M94 and M97 remain upstream opportunity and continuity sources represented through their governed provenance rather than being re-owned by M105.

## Non-goals
M105 does not activate, deliver, schedule, speak, choose a channel, invoke tools, mutate memory, learn automatically, or rewrite any upstream artifact.

## Verification
See `M105_verification.txt` and `tests/test_m105_living_conversation_integration.py`.
