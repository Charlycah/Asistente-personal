# M367.5 — Context State Model

## Propósito

Declarar una vista gobernada del presente cognitivo de ROBY sin crear otro
almacén ni convertir el contexto activo en memoria permanente.

## Autoridad

La autoridad descriptiva única es `context_state_model`, subordinada a
`internal_world_model`.

## Superficies reutilizadas

- `PersonalIdentityRegistry` para sesión e identidad explícita.
- `ConversationalContextContinuity` para continuidad conversacional vigente.
- `UnifiedCognitiveBlackboard` para señales, restricciones y candidatos activos.
- `MentalState` para modo cognitivo y objetivos observables.
- `GoalManager` para objetivos activos.
- `TaskIntelligenceManager` para tareas y trabajo vigente.
- `AmbientContextFoundationEngine` para observaciones consentidas.
- `GlobalContextFusionEngine` para una vista derivada y trazable.
- `ScopeGuard` para límites de lectura, inferencia y acción.

## Límites

M367.5 es de solo lectura y no agrega razonamiento de prioridad.
Representa únicamente el estado actual. No escribe memoria, no cambia objetivos o proyectos,
no autoriza acciones, no añade persistencia y no modifica el runtime.

Una vista derivada del contexto no constituye por sí sola un hecho confirmado.
