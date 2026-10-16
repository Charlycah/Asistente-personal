# ADR-154 — Living Conversation Opportunity Selection

## Decision

M152 selects one governed M151 prioritization result as the declarative candidate for later conversational decision stages.

The component preserves the selected M151 result and its M150 opportunity exactly. Selection is deterministic across priority, confidence, recency, and identifier ordering.

## Boundaries

M152 does not decide to converse, activate Living Conversation, select timing, generate prompts, realize responses, call providers, automate actions, or mutate the platform.
