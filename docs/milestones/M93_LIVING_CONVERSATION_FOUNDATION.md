# M93 — Living Conversation Foundation

## Objective

Open Phase X with a governed decision boundary for ROBY's conversational
presence. M93 determines whether a conversational opportunity justifies an
intervention, should be deferred, requires review, or should remain silent.

## Architecture

```text
M51 Presence / M52 Relationship / M53 Initiative / M54 Social Regulation
                              |
M92 Adaptive Cognition -------+
                              v
                 M93 Living Conversation Manager
                    |-- contextual boundary
                    |-- value and relevance assessment
                    |-- privacy and guest restraint
                    |-- silence / defer / review / intervene
                    `-- immutable auditable decision
```

## Public contracts

- `ConversationOpportunityKind`
- `ConversationDisposition`
- `ConversationContextMode`
- `ConversationOpportunity`
- `LivingConversationContext`
- `LivingConversationPolicy`
- `LivingConversationDecision`
- `LivingConversationDecisionRepository`
- `InMemoryLivingConversationDecisionRepository`
- `LivingConversationManager`

## Governance boundary

M93 does not:

- generate or send conversational content;
- call an LLM or a tool;
- schedule a deferred intervention;
- update memory, relationship state or mental models;
- infer permission from familiarity;
- expose personalized references while guests are present;
- bypass do-not-disturb or sensitive-context review.

## Core invariants

- Presence never creates an obligation to speak.
- Human attention boundaries prevail over conversational value.
- Silence is an explicit, auditable outcome.
- An absent user causes deferral, never automatic scheduling.
- Sensitive or review-required opportunities cannot intervene automatically.
- Guest contexts block personalized source references.
- Decisions are immutable, deterministic for equal inputs and timestamp, and
  persisted behind a repository contract.
- Existing M1–M92 components remain unchanged and optional inputs are linked by
  identifiers rather than mutated.

## Acceptance criteria

- High-value, sufficiently confident opportunities may be marked to intervene.
- Medium-value opportunities defer and low-value opportunities remain silent.
- Explicit user turns receive a proportionate response disposition.
- Do-not-disturb, guest privacy and sensitive contexts override value scores.
- Policy cannot enable unsolicited sensitive content or guest personalization.
- No side effect is performed by the manager.
- Ruff passes and the complete test suite has no regressions.
