# RP.19.3 — Reanudación contextual y resolución autónoma de asuntos

## Objetivo

Extender el Cognitive Agenda Manager canónico para que pueda reanudar asuntos bloqueados y cerrar asuntos resueltos a partir de contexto explícito, sin crear otro scheduler, lifecycle, residente, memoria ni world model.

## Diseño

- `CognitiveAgendaSignal` puede declarar `resolution_conditions` además de las condiciones de reanudación existentes.
- `CognitiveAgendaManager.refresh(...)` recibe hechos contextuales normalizados.
- Un asunto bloqueado vuelve a `active` sólo cuando se cumplen todas sus condiciones de reanudación.
- Un asunto se cierra cuando se cumplen todas sus condiciones de resolución.
- Una fuente puede declarar una política terminal por ausencia mediante `absence_status`.
- La ausencia sólo es terminal cuando todas las fuentes del asunto fueron consultadas con éxito y se declararon autoritativas para esa ausencia.
- Fallas de fuente y fuentes no autoritativas conservan la continuidad persistente.
- El ciclo cognitivo oficial aporta hechos explícitos y hechos derivados del snapshot previo del Cognitive World Model.

## Persistencia

La misma base SQLite de RP.19.1 conserva:

- condiciones de resolución;
- última transición contextual;
- estados terminales y tombstones existentes.

La migración es aditiva y compatible con bases de RP.19.1 y RP.19.2.

## Límites de autoridad

La agenda no interpreta lenguaje libre ni ejecuta acciones. Sólo compara condiciones normalizadas con hechos explícitos publicados por el runtime o por el world model previo. La decisión de cerrar por ausencia pertenece a cada fuente autoritativa.
