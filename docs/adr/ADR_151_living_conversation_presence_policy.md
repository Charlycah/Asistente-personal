# ADR-151 — Living Conversation Presence Policy

## Status
Accepted

## Context
M148 provides a governed Living Conversation awareness representation for stable, transitional, uncertain, and interrupted presence context. The conversational domain needs a separate policy boundary that determines whether this awareness is eligible to be considered by later conversational stages, without turning eligibility into a decision to speak or a timing choice.

## Decision
Introduce M149 as a pure declarative policy layer downstream from M148. It selects the newest valid awareness result, preserves the exact M148 result and state lineage, and evaluates each state as eligible or inhibited. Stable awareness is eligible; transitional, uncertain, and interrupted awareness is inhibited. Partial stable awareness may be accepted or held for review according to explicit configuration.

M149 does not decide to initiate conversation, activate Living Conversation, select timing, generate prompts, realize responses, infer identity/activity/intent, adapt behavior, call providers, automate actions, or mutate the platform.

## Consequences
- Living Conversation gains a stable eligibility contract independent from future decision and timing engines.
- M148 and all upstream Ambient Context contracts remain unchanged.
- Inhibition is explicit and auditable rather than inferred by downstream consumers.
