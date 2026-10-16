# M367.3 — Project Knowledge Model

## Objetivo

Declarar una representación gobernada de proyectos dentro de `internal_world_model`, reutilizando proyectos, tareas, hitos, dependencias, documentación y revisiones de avance existentes.

## Autoridad

`project_knowledge_model` es la única autoridad descriptiva del conocimiento de proyectos. No reemplaza gestores, repositorios ni planificadores especializados.

## Autoridades reutilizadas

- `HouseholdProjectManager`: proyectos explícitos, estado, próximo paso y notas.
- `TaskIntelligenceManager`: tareas, prioridades, estados y referencias.
- `ExecutiveMilestone`: hitos aprobados sin autoridad de ejecución.
- `TaskDependency`: dependencias explícitas entre tareas.
- `DocumentReadingService`: documentación explícita como evidencia grounded.
- `GoalProjectReviewService`: revisión derivada de avance.
- `ScopeGuard`: límites de lectura, edición y ejecución.

## Límites

M367.3 no actualiza proyectos automáticamente, no infiere progreso como hecho, no ejecuta hitos, no convierte documentos en verdad automática, no crea persistencia y no modifica el runtime.
