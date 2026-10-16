# ADR-097 — Conversation Timing Engine

## Estado

Aceptado para M95.

## Contexto

M94 detecta oportunidades conversacionales y M93 conserva la autoridad de gobierno sobre la intervención. Faltaba una frontera explícita para determinar si una oportunidad válida coincide con una ventana temporal apropiada.

## Decisión

Agregar `core.living_conversation.timing` como capa determinista, inmutable y auditable. Recibe una oportunidad M93/M94 y un contexto temporal; produce una recomendación de intervenir ahora, diferir, esperar privacidad, requerir revisión o cancelar.

La evaluación considera presencia, turno explícito, `do_not_disturb`, actividad, carga cognitiva, horario silencioso, invitados, sensibilidad contextual, enfriamiento y presupuesto diario de interrupciones.

## Invariantes

- Detectar una oportunidad no autoriza hablar.
- M95 no genera lenguaje, no agenda y no ejecuta intervenciones.
- `do_not_disturb`, revisión y privacidad prevalecen sobre conveniencia temporal.
- Un turno explícito tiene prioridad temporal, salvo barreras superiores.
- Toda recomendación conserva razones, ventana y caducidad.
- Las oportunidades no permanecen diferidas indefinidamente.

## Consecuencias

M96 podrá generar contenido sólo después de recibir una oportunidad válida y una recomendación temporal compatible. La ejecución futura deberá seguir pasando por la gobernanza de Living Conversation.
