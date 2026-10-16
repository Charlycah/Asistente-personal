# ADR-149 — Living Conversation Presence Consumer

## Status
Accepted

## Context
M146 exposes governed presence-context access without executing consumers. Living Conversation needs a domain-specific, declarative view of that access while preserving the strict separation between context consumption and conversational decision or activation.

## Decision
Introduce M147 as a pure consumer adapter downstream from M146. It selects a valid gateway result for the `living-conversation` consumer and exposes immutable cues containing the source situation kind, situation signal, optional declared conversation context, partial-context marker, confidence, and exact access lineage.

M147 does not decide whether to speak, generate prompts, realize responses, execute consumer logic, infer identity/activity/intent, adapt behavior, call providers, automate actions, or mutate the platform.

## Consequences
- Living Conversation receives a stable domain-facing presence cue.
- M146 and all upstream Ambient Context contracts remain unchanged.
- Future conversational policy milestones may consume M147 without coupling to the publication/delivery pipeline.
