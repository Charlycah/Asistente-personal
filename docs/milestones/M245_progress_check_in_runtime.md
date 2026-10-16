# M245 — Progress Check-In Runtime

M245 adds a deterministic conversational check-in over ROBY's official household
project and long-term goal stores.

## Operational capability

- Project check-ins persist as official project notes.
- Goal and meta check-ins persist through the official progress percentage mutation.
- Existing validation and not-found responses remain authoritative.

## Reuse and boundaries

M245 delegates to the M241 project service and M242 goal service. It uses the same
SQLite stores and the official governed conversation pipeline. It adds no parallel
manager, repository, scheduler, provider, or persistence model.

## Environment contract

`ROBY_PROGRESS_CHECK_IN_ENABLED` controls the interception and defaults to enabled.
The existing `ROBY_HOUSEHOLD_PROJECTS_DB_PATH` and
`ROBY_HOUSEHOLD_GOALS_DB_PATH` settings remain the only persistence paths.
