# M139 — Presence Event Interpretation

## Objective
Interpret governed anonymous M138 presence changes as normalized ambient event semantics.

## Single responsibility
M139 maps the latest valid M138 outcome to an architectural ambient meaning without redetecting change, recomputing continuity, inferring personal activity, or deciding an action.

## Event meanings

- `PRESENCE_BECAME_OBSERVED`
- `PRESENCE_BECAME_UNOBSERVED`
- `AMBIENT_OCCUPANCY_SHIFTED`
- `TRANSIENT_PRESENCE_SIGNAL`
- `PRESENCE_CERTAINTY_CHANGED`
- `PRESENCE_CONTINUITY_LOST`

Stable M138 no-change results are represented explicitly as `NO_EVENT` and suppressed.

## Architectural chain

`M134 Ambient Context Foundation`
→ `M135 Ambient Observation Resolution`
→ `M136 Presence Understanding`
→ `M137 Presence Continuity`
→ `M138 Presence Change Detection`
→ `M139 Presence Event Interpretation`

## Explicit exclusions
M139 does not perform change detection, continuity analysis, identity inference, biometrics, precise person counting, activity or intent inference, individual or movement tracking, sensor access, provider access, platform mutation, decision-making, or automation.

## Validation target

- Ruff clean.
- Focused M139 tests passing.
- Complete regression suite passing.
- Clean Git working tree after commit.
