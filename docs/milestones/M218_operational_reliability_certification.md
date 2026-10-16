# M218 — Operational Reliability Certification

M218 converts bounded M217 stress evidence into a formal operational reliability certificate.

## Capabilities

- Identity-bound consumption of M217 stress reports.
- Explicit criteria for coverage, stress outcome, task-failure rate, execution availability, and trace lineage.
- Configurable minimum-cycle and maximum-failure-rate thresholds.
- Deterministic `certified`, `conditional`, and `rejected` outcomes.
- Immutable certificate identity and exact source lineage.
- Unified cognitive blackboard publication.
- Official runtime composition immediately after M217.

## Boundaries

M218 does not generate load, rerun stress scenarios, execute recovery, restart providers, scale infrastructure, approve production deployment, or perform the M219 production-readiness assessment.

## Validation

- Focused tests: 16 passed.
- Ruff: all checks passed.
- Complete suite: 5,547 passed.
- Regressions: zero.
