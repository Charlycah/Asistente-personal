# M380 — Organized Work Model

## Propósito

Consolidar objetivos, proyectos y tareas bajo la fachada única de organización personal sin reemplazar sus autoridades existentes.

## Autoridad

`PersonalOrganizationAuthority` continúa siendo la autoridad canónica de la Fase IV. `OrganizedWorkAuthority` es una vista subordinada de integración y no un nuevo cerebro, planificador o repositorio.

## Contratos

- `OrganizedWorkKind`
- `OrganizedWorkReference`
- `OrganizedWorkSnapshot`
- `OrganizedWorkAuthority`

Las referencias expresan relaciones explícitas entre objetivo, proyecto y tarea. El snapshot rechaza duplicados y referencias parentales inexistentes.

## Límites

M380 no crea, modifica ni ejecuta objetivos, proyectos o tareas. No añade persistencia, memoria, LLM, agentes, planificación paralela ni cambios de runtime.
