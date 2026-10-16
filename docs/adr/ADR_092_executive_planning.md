# ADR-092 — Executive Planning

## Status

Accepted for M90.

## Context

ROBY already has operational planning for a cognitive turn, action proposals for
registered capabilities, task intelligence and governed autonomy. Those layers
do not provide a stable strategic representation of long-lived objectives,
success criteria, dependencies and constraints across multiple horizons.

M85–M89 also provide experience, mental models, metacognitive evaluation,
reflection and governed knowledge-evolution proposals. A higher planning layer
must be able to reference those artifacts without treating them as authority to
execute work.

## Decision

Introduce `core.adaptive_cognition.executive_planning` as an immutable,
revisioned strategic planning boundary. Executive plans contain objectives,
measurable success criteria, ordered milestones, explicit dependencies,
constraints and traceable references to M86, M88 and M89 artifacts.

Plan creation and every lifecycle transition produce a new revision. Long-term
plans and plans containing critical objectives require explicit review. Status
`active` means the strategy is currently considered, not that milestones are
being executed.

M90 does not schedule tasks, invoke tools, grant permissions, mutate knowledge
or bypass M69/M70 governance.

## Consequences

- Strategic planning is separated from turn-level and tool-level planning.
- Historical plans remain auditable through immutable revisions.
- M91 can coordinate approved plans without inheriting execution authority.
- Existing goal, task and autonomy contracts remain unchanged.
