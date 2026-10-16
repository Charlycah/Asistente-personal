# M397.7 — Health / Readiness

## Purpose

M397.7 defines observable health and readiness facts for a governed connectivity
session without introducing heartbeat execution, timers, polling or network I/O.

## Core rule

> **Connected is not ready; ready is a derived governed fact.**

## Health

`ConnectivityHealthState` represents `UNKNOWN`, `HEALTHY`, `DEGRADED` and
`UNAVAILABLE`. Health is observational and grants no admission, authority or execution
permission.

## Readiness

`ReadinessState` is explicit: `NOT_READY` or `READY`.

A connectivity context may be `READY` only when all of these are true:

1. peer identity is authenticated;
2. residence membership is admitted;
3. logical session is `ACTIVE`;
4. health is `HEALTHY`.

Any missing prerequisite produces `NOT_READY`.

## State separation

M397.7 preserves:

`AUTHENTICATED != ADMITTED != ACTIVE != HEALTHY != READY`

and:

`CONNECTED != READY`

Readiness is not residence identity, admission, capability authority or command
authorization.

## Failure semantics

A peer may become `DEGRADED` or `UNAVAILABLE` without changing its `ResidenceId`,
admission history or ROBY's primary-home continuity.

## Future heartbeat

A later increment may define how health evidence is produced through a governed
heartbeat or probe. M397.7 defines only the resulting facts and invariants, not the
mechanism.

## Runtime and transport boundary

M397.7 introduces no heartbeat loop, timer, timeout scheduler, polling task, ping,
socket, HTTP request, WebSocket frame, background thread or runtime wiring.

## Exit criterion

M397.7 is complete when health and readiness are immutable, fail-safe, derived only
from explicit governed facts, transport-neutral and regression-tested.

> **ROBY may know that a window exists without pretending that the window is ready to
> use.**
