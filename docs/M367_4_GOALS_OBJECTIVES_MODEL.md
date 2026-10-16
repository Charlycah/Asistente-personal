# M367.4 — Goals & Objectives Model

M367.4 reconcilia las superficies existentes de objetivos bajo
`goals_objectives_model`, subordinada a `internal_world_model`.

Reutiliza `GoalManager`, `HouseholdGoalManager`, `ExecutiveObjective`,
`CognitivePriorityPolicy`, `GoalBlocker`, `GoalProjectReviewService` y
`ScopeGuard`.

El modelo representa metas, prioridades, bloqueos y revisiones, pero no crea
objetivos automáticamente, no modifica prioridades silenciosamente y no autoriza ejecución. Representar una meta no equivale a actuar sobre ella.
