# M154 — Living Conversation Conversation Eligibility Decision

## Responsibility
Convert governed M153 readiness into a declarative eligibility decision for later Living Conversation stages.

## Inputs
- Owner-scoped immutable M153 readiness results.
- A request flag indicating whether an eligibility decision is required.

## Outputs
- `ELIGIBLE` for complete readiness.
- `ELIGIBLE_PARTIAL` for allowed partial readiness.
- `NOT_ELIGIBLE` for not-ready input.
- Review, blocked, and not-applicable outcomes where governance requires them.

## Determinism
Candidate ordering uses readiness class, confidence, recency, and deterministic readiness identifier.

## Explicit non-goals
M154 does not start conversations, activate Living Conversation, select timing, generate prompts, realize responses, call providers, automate actions, or mutate the platform.
