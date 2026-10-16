# RP.19.2 — Activación inteligente de la agenda cognitiva

La persistencia de RP.19.1 conserva asuntos. RP.19.2 decide cuál de esos asuntos está listo para ocupar el ciclo cognitivo.

## Contrato dual

La agenda publica dos conceptos distintos:

- `primary_focus`: el asunto mejor posicionado en la vista ejecutiva, aunque esté bloqueado.
- `activated_focus`: el asunto elegible que efectivamente alimenta deliberación y continuidad cognitiva.

`effective_focus` mantiene compatibilidad con snapshots históricos creados manualmente por pruebas o integraciones anteriores.

## Elegibilidad

Los asuntos activos son elegibles. Los asuntos en observación requieren el umbral de urgencia configurado. Los asuntos bloqueados, cerrados o archivados no se activan.

## Arbitraje

El arbitraje parte del score canónico de prioridad, urgencia y relevancia. Luego aplica:

- una penalización decreciente cuando el mismo asunto fue activado recientemente;
- una bonificación acotada según el tiempo que el asunto lleva esperando atención.

Esto evita monopolio cognitivo sin desordenar la agenda ni reemplazar el scheduler oficial.

## Persistencia y lifecycle

La misma tabla `cognitive_agenda_items` incorpora `last_activated_at` y `activation_count`. La inicialización SQLite migra automáticamente bases creadas por RP.19.1. El manager se restaura desde el wiring oficial y no posee lifecycle propio.

## Flujo descendente

`CognitiveAgendaReasoner`, `CognitiveThoughtStream` y `ContinuousInternalCognitiveLoop` consumen `effective_focus`. Por lo tanto, un asunto bloqueado puede seguir visible y persistente sin generar deliberación, hipótesis, world model ni episodios falsos.
