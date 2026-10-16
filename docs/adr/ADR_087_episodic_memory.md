# ADR-087 — Governed Episodic Memory

## Status

Accepted for M85.

## Context

ROBY already had generic persistence, cognitive recall, working memory and experiential learning. None of those components represented a bounded experience with temporal order, governed references, outcome and immutable revision history. Reusing them as episodic memory would collapse distinct concepts and allow experience to be mistaken for fact or learning.

## Decision

Introduce `core.adaptive_cognition` as the Phase IX boundary and implement M85 through immutable episodes, events and references.

An episode is an append-only temporal record. It may preserve observations, user input, context, inference, decisions, actions, outcomes and feedback, but it does not determine truth, learn a rule, update knowledge or authorize action.

The repository stores every immutable revision. Recall is deterministic and constrained by owner, Scope Guard domain, lifecycle status, sensitivity, tags, time, importance and limit.

M84 results may be captured as completed or review-required episodes with direct references to the reasoning result, context, Decision Record and Explainable Answer.

## Consequences

- Experience remains distinct from evidence, claims, knowledge and learned abstractions.
- M86–M89 can consume episodes without depending on legacy memory storage details.
- Audit history is preserved at the aggregate revision and event levels.
- Sensitive episodes are excluded from recall unless explicitly requested.
- Cognitive Pipeline integration remains optional and backward compatible.
- Persistent repository implementations can be added behind the repository protocol.
