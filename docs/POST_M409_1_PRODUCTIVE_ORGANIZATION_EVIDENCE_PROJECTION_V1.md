# Post-M409.1 — Productive Organization Evidence Projection Foundation v1

## Objetivo

Cerrar únicamente la frontera de evidencia entre datos organizativos ya admitidos y el contrato M391.5. La foundation proyecta Tasks, Goals, Projects y Reminders existentes a `PersonalOrganizationItem` sin crear otra autoridad, repositorio, runtime o inteligencia paralela.

## Autoridad y posición arquitectónica

`PersonalOrganizationAuthority` permanece como única fachada canónica del dominio. `ProductiveOrganizationEvidenceProjection` es una proyección subordinada, pura, stateless, determinista y read-only. No adquiere authority semantics.

Las autoridades/services/managers productivos existentes siguen siendo propietarios de sus datos. La proyección recibe objetos de dominio ya obtenidos por la composición existente; no abre SQLite ni consulta repositories.

## Contrato v1

La salida es exclusivamente `tuple[PersonalOrganizationItem, ...]`, destinada a `IntelligentPersonalOrganizationView` M391.5.

### Tasks

- `item_id <- task_id`
- `capability <- TASKS`
- `title <- title`
- `urgency <- urgency / 10.0`
- `importance <- importance / 10.0`
- `blocked <- status == BLOCKED`
- `source_reference <- task:<task_id>`

No se transporta `Task.priority_score()`. `goal_alignment`, `context_relevance`, `deadline_proximity`, `safety_risk`, `user_declared` y `conflicting` permanecen neutrales.

### Goals

Se proyectan identidad, capability, título y provenance para estados ACTIVE/PAUSED. Todas las señales cognitivas permanecen neutrales. `progress_percent`, `target_date`, `next_step` y links no se reinterpretan.

### Projects

Se proyectan identidad, capability, título y provenance para estados ACTIVE/PAUSED. Todas las señales cognitivas permanecen neutrales. No se infiere bloqueo desde ausencia de `next_step`.

### Reminders

Sólo se admiten reminders `PENDING`. Se proyectan identidad, capability, título y provenance. `due_at` no se transforma aún en `deadline_proximity` ni urgencia.

## Determinismo y provenance

La salida se ordena establemente por capability e `item_id`. Cada objeto conserva provenance inmediata mediante `task:`, `goal:`, `project:` o `reminder:`. IDs duplicados entre fuentes se rechazan antes de entrar a M391.5.

## Fronteras congeladas

Foundation v1 es read-only y no crea, modifica, completa, cancela ni persiste Tasks, Goals, Projects o Reminders. No llama `PriorityReasoning` directamente; M391.5 conserva esa responsabilidad.

Queda en **NO-GO** dentro de v1: M391.6 / Canonical Decision integration, deadline normalization, goal alignment, context relevance, safety inference, conflict inference, Agenda, Notes, Initiative, Proactive Care, autonomous execution, background processing, repositorios/DB nuevos, authority nueva, M410 y cualquier cambio en Residential Remote Presence/networking.

## Cierre esperado

La foundation se considera cerrable sólo con Ruff limpio, suite completa sin regresiones y documentación canónica sincronizada. Su existencia no autoriza automáticamente una fase M391.6 posterior.
