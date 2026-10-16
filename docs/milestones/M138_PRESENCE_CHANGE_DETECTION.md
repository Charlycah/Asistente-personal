# M138 — Presence Change Detection

## Objective
Detect publishable anonymous ambient presence changes from governed M137 continuity results.

## Single responsibility
M138 decides whether the latest valid M137 outcome is:

- a publishable change;
- stable continuity that must be suppressed;
- insufficient or uncertain input requiring review;
- invalid input that must be blocked;
- outside the declared detection scope.

## Change kinds

- `APPEARANCE`
- `DISAPPEARANCE`
- `OCCUPANCY_VARIATION`
- `TRANSIENT_VARIATION`
- `UNCERTAIN_VARIATION`
- `CONTINUITY_BREAK`

## Architectural chain

`M134 Ambient Context Foundation`
→ `M135 Ambient Observation Resolution`
→ `M136 Presence Understanding`
→ `M137 Presence Continuity`
→ `M138 Presence Change Detection`

## Explicit exclusions
M138 does not perform identity inference, biometrics, precise person counting, activity inference, individual tracking, movement tracking, sensor access, provider access, platform mutation, or automation.

## Validation target

- Ruff clean.
- Focused M138 tests passing.
- Complete regression suite passing.
- Clean Git working tree after commit.
