# M81 — Conflict & Uncertainty

## Objective

Add deterministic conflict detection, governed resolution and explicit uncertainty assessment over M78 claims and M80 inference outputs.

## Delivered

- `ConflictType`, `ConflictSeverity` and immutable `Conflict`.
- `ResolutionStatus` and immutable `ResolutionDecision`.
- `UncertaintyFactor` and `ConfidenceAssessment`.
- `ConflictResolutionPolicy`.
- `ConflictAnalysis` with stable fingerprint.
- `ConflictResolutionManager`.
- Detection of incompatible active values for the same owner, subject and predicate.
- Exclusion of stale and superseded claims from active conflict detection.
- Deterministic precedence by lifecycle status, origin, confidence, recency and stable identity.
- Human review for high-severity conflicts.
- Confidence penalties and caps for unresolved or review-required conflicts.
- Optional inclusion of M80 applied inference claims.

## Invariants

- Conflict resolution never mutates evidence, claims or inference runs.
- High-severity conflicts are not silently resolved.
- Unresolved conflicts cannot increase confidence.
- Same input state yields the same conflicts, decisions and analysis identifier.
- Conflict analysis does not create Decision Records or external actions.

## Deferred

- Persistent Decision Records: M82.
- User-facing explanation rendering: M83.
- End-to-end orchestration: M84.
