# M366.4 — Procedural Memory

M366.4 reconcilia las superficies procedimentales existentes de ROBY sin crear
un almacén paralelo ni habilitar comportamiento nuevo.

## Autoridad canónica

Todas las capas permanecen subordinadas a `memory_gateway`:

- `GovernedPlanModel`: planes gobernados, dependencias y autorizaciones.
- `RoutineHabitManager`: rutinas y hábitos supervisados.
- `TaskIntelligenceManager`: tareas, dependencias y pasos operativos.

## Frontera de seguridad

**recordar un procedimiento no autoriza su ejecución.** La memoria procedural
puede describir cómo realizar una actividad, pero la autorización, selección y
ejecución continúan perteneciendo a sus autoridades operativas existentes.

M366.4 no añade persistencia, aprendizaje automático, promoción automática,
conexión nueva al runtime ni cambios al planner.
