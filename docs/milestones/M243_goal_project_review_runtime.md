# M243 — Goal and Project Review Runtime

M243 adds a deterministic review over the official household project and goal stores.
It identifies active items without a next step and active items whose last update exceeds
the configured staleness threshold. The review is available on demand through the
official conversation pipeline and is also included in the daily household briefing.

Configuration:

- `ROBY_GOAL_PROJECT_REVIEW_ENABLED=true`
- `ROBY_GOAL_PROJECT_REVIEW_STALE_DAYS=14`
- `ROBY_GOAL_PROJECT_REVIEW_MAX_ITEMS=8`
- `ROBY_GOAL_PROJECT_REVIEW_INCLUDE_IN_BRIEFING=true`

Certification: Ruff clean; 6026 tests passed; 0 skipped.
