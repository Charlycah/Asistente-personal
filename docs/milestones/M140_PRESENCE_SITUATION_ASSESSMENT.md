# M140 — Presence Situation Assessment

## Objective
Assess governed anonymous M139 presence-event semantics as normalized ambient situations.

## Single responsibility
M140 maps the latest valid M139 interpretation to a situational class without reinterpreting the event, recomputing continuity, detecting change, inferring personal activity, or deciding a response.

## Situation classes

- `STABLE`
- `TRANSITION`
- `UNCERTAIN`
- `INTERRUPTED`

## Situation signals

- `STABLE_PRESENCE`
- `PRESENCE_APPEARED`
- `PRESENCE_DISAPPEARED`
- `OCCUPANCY_CHANGED`
- `TRANSIENT_CHANGE`
- `CERTAINTY_CHANGED`
- `CONTINUITY_INTERRUPTED`

Stable M139 no-event results are assessed explicitly and suppressed.

## Architectural chain

`M134 Ambient Context Foundation`
→ `M135 Ambient Observation Resolution`
→ `M136 Presence Understanding`
→ `M137 Presence Continuity`
→ `M138 Presence Change Detection`
→ `M139 Presence Event Interpretation`
→ `M140 Presence Situation Assessment`

## Explicit exclusions
M140 does not perform event interpretation, change detection, continuity analysis, identity inference, biometrics, precise person counting, activity or intent inference, individual or movement tracking, response decision-making, sensor access, provider access, platform mutation, or automation.

## Validation target

- Ruff clean.
- Focused M140 tests passing.
- Complete regression suite passing.
- Clean Git working tree after commit.
