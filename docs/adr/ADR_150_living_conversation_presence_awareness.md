# ADR-150 — Living Conversation Presence Awareness

## Status
Accepted

## Context
M147 adapts governed M146 gateway access into Living Conversation presence cues. The conversational domain needs a stable awareness representation describing whether presence context is available, stable, transitional, uncertain, interrupted, complete, and sufficiently confident, without coupling downstream policies to Ambient Context internals.

## Decision
Introduce M148 as a pure awareness layer downstream from M147. It selects the newest valid consumer result and creates immutable awareness states that preserve the exact source result and cue lineage. Situation kinds are normalized into stable, transitional, uncertain, and interrupted awareness kinds with explicit consistency flags.

M148 does not decide whether to speak, activate conversation, choose timing, generate prompts, realize responses, infer identity/activity/intent, adapt behavior, call providers, automate actions, or mutate the platform.

## Consequences
- Living Conversation receives a stable internal awareness contract.
- M147 and all upstream Presence Context contracts remain unchanged.
- Future timing or conversational-policy milestones can consume M148 without depending on the Ambient Context pipeline.
