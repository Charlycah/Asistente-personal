# M95 — Conversation Timing Engine

## Objetivo

Determinar cuándo una oportunidad conversacional gobernada puede aprovecharse sin convertir la detección en una interrupción automática.

## Alcance

- Estados de actividad conversacional.
- Contexto temporal inmutable.
- Política configurable de carga, frecuencia, horario y caducidad.
- Recomendaciones `intervene_now`, `defer`, `wait_for_private_context`, `review_required` y `cancel`.
- Ventana más temprana y expiración.
- Persistencia por contrato y repositorio en memoria.
- Integración directa con `ConversationOpportunity` y `LivingConversationContext`.

## Reglas principales

1. Revisión, sensibilidad y privacidad tienen precedencia.
2. `do_not_disturb` siempre difiere.
3. La ausencia, el foco, la actividad ocupada y la carga alta difieren.
4. Un turno explícito tiene prioridad sobre carga, actividad y horario silencioso.
5. Invitados bloquean intervenciones espontáneas, no respuestas explícitas.
6. El presupuesto diario agotado cancela la oportunidad espontánea.
7. El intervalo mínimo evita intervenciones consecutivas.
8. Una ventana posterior a la caducidad cancela el candidato.

## Fuera de alcance

- Generación de texto.
- Llamadas a LLM.
- Ejecución o envío de mensajes.
- Programación de tareas o timers.
- Mutación de memoria, presencia o relación.
- Selección definitiva de contenido.

## Integración

```text
M94 detecta -> M95 recomienda ventana -> M93 gobierna -> futuros milestones generan/ejecutan
```

## Criterios de aceptación

- API pública exportada desde `core.living_conversation`.
- Decisiones inmutables, trazables y persistibles.
- Compatibilidad completa con M1–M94.
- Ruff limpio.
- Suite completa sin regresiones.
