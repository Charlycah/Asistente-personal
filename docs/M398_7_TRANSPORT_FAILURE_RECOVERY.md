# M398.7 — Transport Failure & Recovery

## Purpose

Classify physical transport failures and define bounded recovery eligibility without
granting recovery code any authority over M397 identity, authentication, admission,
logical-session lifecycle, readiness or action execution.

## Permanent recovery invariants

- **M398-RC00 — Physical failures only.** Recovery observes carrier failures, not
  cognitive or residence authority.
- **M398-RC01 — Classification before action.** Failure is represented explicitly
  before any recovery decision is made.
- **M398-RC02 — Bounded retry budget.** Retry eligibility is constrained by an
  explicit `TransportRetryPolicy`.
- **M398-RC03 — No implicit infinite retry.** Attempts outside the configured budget
  are rejected.
- **M398-RC04 — Protocol-invalid input is not auto-retried.** Invalid frames and
  premature EOF fail closed instead of entering retry loops.
- **M398-RC05 — Assessment is pure.** `assess_transport_recovery` performs no I/O and
  creates no socket.
- **M398-RC06 — Redial requires permission.** `LocalTcpRecovery.redial()` operates
  only after an explicit `RETRY_ALLOWED` assessment.
- **M398-RC07 — Redial is physical only.** A successful redial creates only a new TCP
  carrier; it does not create or reactivate an M397 session.
- **M398-RC08 — No authority escalation.** Failure observations, assessments and
  recovery always report no action authority.
- **M398-RC09 — No hidden scheduler.** Recovery contains no sleep loop, background
  worker, timer or autonomous retry engine.
- **M398-RC10 — M397 remains authoritative.** Recovery cannot import or mutate
  authentication, admission, residence or session lifecycle state.
- **M398-RC11 — End-to-end use remains separate.** This increment does not yet bind
  recovery into an end-to-end governed residence channel.

## Failure categories

M398.7 distinguishes connection refused, timeout, connection reset, premature EOF,
invalid frame and generic OS errors. The categories are transport observations only.
They do not redefine the M397 failure/revocation assessment.

`INVALID_FRAME` and `PREMATURE_EOF` are deliberately not automatically retried.
Connection-level failures may be eligible for bounded physical retry until the
configured attempt budget is exhausted.

## Recovery model

The policy layer is pure and declarative. `LocalTcpRecovery` can perform one explicitly
permitted redial through the existing M398.6 `LocalTcpDialer`. There is no automatic
retry loop, backoff scheduler or session restoration mechanism.

A redial does not imply authentication, admission, readiness or continuity of the prior
logical session. Any logical continuation must independently satisfy M397.

The first end-to-end governed residence channel remains reserved for M398.8.

## Validation

The corrected M398.6 `core/physical_transport/__init__.py` is integrated into this
baseline. Regenerate M361 and require Ruff plus the complete pytest suite without
regressions.
