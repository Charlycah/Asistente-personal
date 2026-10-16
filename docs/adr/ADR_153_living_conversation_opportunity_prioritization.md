# ADR-153 — Living Conversation Opportunity Prioritization

## Status
Accepted.

## Decision
M151 ranks governed M150 presence opportunities into high, medium, or deferred priority. It preserves exact source opportunities and emits an immutable deterministic ordering.

## Boundaries
M151 does not decide whether to converse, activate Living Conversation, select timing, generate prompts, realize responses, call providers, automate actions, or mutate the platform.

## Consequences
Opportunity ranking is separated from later conversational decision and timing layers, preserving low coupling and auditability.
