# M141 — Presence Context Integration

## Responsibility
Integrate a governed M140 presence-situation assessment with explicitly declared
context dimensions.

## Inputs
- M140 assessment results.
- Optional declared device context.
- Optional declared conversation context.
- Optional declared spatial context.
- Optional declared temporal context.

## Outputs
- Fully integrated context when the configured dimension threshold is met.
- Partial context when at least one dimension is available but the threshold is not met.
- Review, blocked, or not-applicable results when governance requirements fail.

## Invariants
- The selected M140 result is preserved exactly.
- Ambient lineage must remain singular.
- Missing context is never inferred.
- Results are immutable, deterministic, deduplicated, freshness-controlled, and
  owner-scoped.
- Identity, biometrics, precise counting, activity, intent, tracking, response decisions,
  behavior adaptation, sensor access, and automation remain disabled.
