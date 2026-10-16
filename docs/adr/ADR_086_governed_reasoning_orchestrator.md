# ADR-086 — Governed Reasoning Orchestrator

## Status

Accepted.

## Context

M77–M83 provide evidence normalization, claims, governed context, deterministic inference, conflict and uncertainty analysis, immutable Decision Records and public explanations. A final integration boundary is required so callers do not coordinate those subsystems independently or bypass governance order.

## Decision

Introduce `core.governed_reasoning.orchestrator` with:

- `GovernedReasoningPolicy`;
- `GovernedReasoningStatus`;
- immutable `GovernedReasoningResult`;
- `GovernedReasoningOrchestrator`;
- `GovernedReasoningManager`.

The mandatory execution order is:

1. assemble governed context;
2. execute registered inference rules;
3. analyze conflicts and uncertainty;
4. classify conclusion, abstention, block or review;
5. persist an immutable Decision Record;
6. render an Explainable Answer.

The orchestrator does not execute tools, mutate source repositories, promote inferred claims to facts or grant action permission. Integration with `CognitivePipeline` is optional and backward compatible. The pipeline receives only the final result reference and public prompt guidance.

## Consequences

- M77–M83 have one stable public coordination boundary.
- Governance cannot be silently reordered by normal callers.
- Abstention and block remain successful, auditable outcomes.
- Decision and explanation identifiers remain available for tracing.
- Reasoning remains separate from autonomous action authorization.
- Existing pipeline construction remains valid when M84 is absent.

## Deferred

- Persistent database implementations for claims and decisions.
- Multi-pass or recursive inference.
- Automatic action proposal generation.
- External source retrieval during orchestration.
