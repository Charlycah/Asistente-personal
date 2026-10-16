# ADR M229 — Always-On Personal Runtime

## Status

Accepted.

## Context

ROBY already owns a long-lived lifecycle, heartbeat supervision, presence models,
initiative governance and battery concepts. The missing operational link was a
real host signal capable of producing a useful unsolicited intervention while
the conversation console is idle.

## Decision

M229 introduces a resident battery-awareness service using the pattern:

```
native sensor -> snapshot -> policy -> anti-repetition -> ROBY intervention
```

The service starts and stops with the existing conversation runtime. It runs in
a daemon thread, reads Windows power state without an optional dependency, and
uses Linux sysfs when available. Missing hardware and sensor failures are silent
and must never block ROBY.

A low-battery message is emitted only when the machine is not charging, at or
below the configured threshold. Hysteresis starts a new episode after charging
or sufficient recovery; a cooldown prevents repeated interruptions.

## Consequences

- ROBY can initiate a useful message without a user turn.
- No cognitive domain is duplicated.
- No cloud service or new dependency is required.
- The same sensor/event/policy/intervention pattern can later serve reminders,
  weather, vision and ambient context.
- Closing the console still stops the process in M229; background startup and
  Windows session integration remain later steps in the master plan.
