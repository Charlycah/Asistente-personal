# ADR-152 — Living Conversation Presence Opportunity

## Status
Accepted

## Context
M149 declares whether presence context is eligible or inhibited for later conversational consideration. A separate layer is required to express a potential presence-based conversational opportunity without deciding to converse, selecting timing, or realizing an intervention.

## Decision
Introduce M150 as a pure declarative opportunity layer downstream from M149. It selects the latest governed policy result and emits an immutable available, partially available, or inhibited opportunity while preserving exact source lineage.

## Constraints
M150 cannot decide, activate, schedule, prompt, respond, infer identity/activity/intent, adapt behavior, call providers, automate, or mutate the platform.

## Consequences
Living Conversation gains an explicit opportunity artifact while decision and execution remain reserved for later milestones.
