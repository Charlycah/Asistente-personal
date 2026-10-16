# M397.8 — Failure + Revocation

## Purpose

M397.8 defines how connectivity reacts safely to failure and canonical residence
revocation without allowing Connectivity Domain to own residence membership.

## Core rule

> **Failure affects connectivity; revocation invalidates continued use of the
residence.**

## `ConnectivityFailureDisposition`

The explicit consequence is one of:

- `NONE`
- `DEGRADED`
- `TERMINATE`
- `REVOKED`

## `ConnectivityFailureAssessment`

An immutable assessment combines:

- session identity;
- peer `ResidenceId`;
- canonical admission-verification result;
- connectivity health;
- resulting readiness;
- resulting session lifecycle consequence;
- non-secret reason text.

A failure/revocation assessment can never remain `READY`.

## Revocation semantics

If M396 reports canonical membership as `REVOKED`, M397 must terminate the logical
session with `SessionTerminationReason.REVOKED`.

M397 does not create the revocation and does not modify residence history.

Authentication remains historically true as evidence of identity, but it cannot
override revocation.

## Admission failure

An authenticated peer that is not canonically `ADMITTED` cannot continue as a valid
connectivity session. The safe result is termination and `NOT_READY`.

## Health failure

`DEGRADED` health removes readiness but does not itself revoke residence membership.

`UNAVAILABLE` health terminates the current logical session safely. The residence may
remain admitted and reconnect later through a new session.

## Identity/session mismatch

If admission verification belongs to another session or another `ResidenceId`, M397.8
fails closed and terminates the current session.

## Primary-home preservation

Failure or revocation of an extended residence never promotes another residence, never
moves `PRIMARY_HOME`, and never changes ROBY's cognitive authorities.

The laptop/home continuity established by M396 remains untouched.

## Authority boundary

M397.8 cannot:

- create or delete `ResidenceRevocationRecord`;
- change `ResidenceAdministrativeState`;
- re-admit a revoked residence;
- promote or migrate the home;
- execute remote shutdown or wipe;
- alter credentials;
- change cognitive, memory or capability authority.

It only derives the safe connectivity consequence from already-governed facts.

## Runtime and transport boundary

M397.8 introduces no socket close operation, heartbeat executor, timeout scheduler,
network listener, remote command or runtime wiring.

## Exit criterion

M397.8 is complete when failure and revocation consequences are explicit, fail-closed,
read-only with respect to M396, transport-neutral and regression-tested.

> **A broken window may close; a revoked window stops being usable. Neither event
> rewrites the house.**
