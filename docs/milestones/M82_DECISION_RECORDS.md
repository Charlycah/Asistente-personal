# M82 — Decision Records

## Objective

Persist every governed reasoning outcome as an immutable, traceable and reviewable audit record without copying source documents or exposing unrestricted internal reasoning.

## Delivered

- `DecisionStatus`, `DecisionOutcome` and `ReviewStatus`.
- Immutable `DecisionEvidenceLink`, `DecisionClaimLink` and `DecisionRuleLink`.
- Immutable `ReviewEvent`.
- Immutable `DecisionRecord` with stable SHA-256 identity.
- `DecisionRecordRepository` protocol.
- `InMemoryDecisionRecordRepository`.
- `DecisionRecordManager`.
- Automatic classification of completed, inconclusive, blocked, conflict-unresolved and review-required outcomes.
- Links to evidence fingerprints, claim revisions, rule versions and conflict identifiers.
- Confidence, limitations, assumptions and Scope Guard status preservation.
- Human approval or rejection through new superseding records.
- Public `to_dict()` audit representation for M83.

## Invariants

- Decision Records are immutable.
- Duplicate record identifiers are rejected.
- Human review never rewrites the original record.
- Pending review is only valid for review-required decisions.
- Blocked decisions have a blocked public outcome.
- References preserve evidence fingerprints, claim revisions and rule versions.
- Decision Records do not execute actions or modify M77–M81 inputs.
- Decision Records store public audit facts, not unrestricted chains of thought.

## Deferred

- User-facing explanation rendering: M83.
- Cognitive Pipeline integration and full orchestration: M84.
- Durable repository implementation: future milestone after contract stabilization.
