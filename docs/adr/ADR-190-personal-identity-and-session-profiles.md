# ADR-190 — Personal Identity and Session Profiles

## Status

Accepted.

## Decision

ROBY's official runtime selects an explicit persisted identity profile before bootstrap. Runtime sessions are immutably bound to a profile. Carlos, his wife, and shared family context are distinct profiles; shared context is opt-in and never formed by silently combining private identities.

## Consequences

- Lifecycle state is scoped by profile and session.
- Existing owner-based memory separation remains intact.
- A session cannot migrate between identities.
- Profile names can be configured locally without changing source code.
- Profile and session metadata are private operational data, not cognitive memory.
