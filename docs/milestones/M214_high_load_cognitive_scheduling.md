# M214 — High-Load Cognitive Scheduling

M214 adds recovery-aware admission control to ROBY's unified cognitive architecture.

## Delivered

- Immutable high-load schedules with deterministic identities and lineage.
- Four load bands: `nominal`, `elevated`, `high`, and `saturated`.
- Three admission dispositions: `admit`, `defer`, and `shed`.
- Capacity-aware ordering that preserves M205 priorities.
- Mandatory tightening when M213 reports `stabilizing` or `held`.
- Blackboard publication through `high_load_cognitive_schedule`.
- Official runtime placement immediately after M213.

## Operational boundary

M214 decides which cognitive work may enter the governed execution path under pressure. It does not execute tasks, create worker pools, perform parallel work, invoke tools, restart providers, or mutate infrastructure. M216 retains the future authority for concurrent cognitive execution.

## Validation

- Focused M214 tests: 16 passed.
- Ruff: all checks passed.
- Full suite: 5484 passed.
- Regressions: zero.
