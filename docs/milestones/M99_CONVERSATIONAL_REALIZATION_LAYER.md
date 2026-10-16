# M99 — Conversational Realization Layer

## Objetivo
Convertir una contribución intelectual M98 ya gobernada, temporalmente habilitada y estructurada en una expresión conversacional final, acotada, natural, trazable y neutral respecto del canal, sin entregarla ni ejecutarla.

## Alcance
- Actos conversacionales `answer`, `question`, `observation`, `connection` y `continuation`.
- Registros `concise`, `natural` y `deliberate`.
- Segmentos ordenados y proyección final `text`.
- Aperturas deterministas según acto y contexto explícito.
- Tratamiento opcional por nombre del propietario.
- Inclusión opcional de título.
- Normalización de puntuación terminal.
- Límites configurables de caracteres y segmentos.
- Estados `ready`, `abstained` y `review_required`.
- Persistencia mediante contrato y repositorio en memoria.

## Contratos principales
- `ConversationalAct`
- `ConversationalRegister`
- `ConversationalRealizationStatus`
- `ConversationalRealizationPolicy`
- `ConversationalRealizationRequest`
- `ConversationalRealization`
- `ConversationalRealizationRepository`
- `ConversationalRealizationLayer`

## Invariantes
1. Toda realización referencia exactamente una contribución M98.
2. El propietario debe coincidir con el propietario gobernado por M93.
3. Sólo una contribución M98 `ready` puede producir texto.
4. `abstained` y `review_required` nunca contienen segmentos conversacionales.
5. Las fuentes se conservan sin alteración.
6. Una pregunta exige cierre interrogativo por defecto.
7. Los límites de caracteres y segmentos se aplican antes de exponer texto.
8. La realización es inmutable, identificable y auditable.
9. M99 no inventa conocimiento ni vuelve a decidir gobernanza, timing o profundidad.
10. M99 no entrega mensajes, no selecciona canal, no habla, no agenda, no usa herramientas y no modifica memoria.

## Integración

```text
M93 gobernanza
      +
M95 timing
      +
M96 borrador
      +
M98 contribución intelectual
      ↓
M99 realización conversacional neutral al canal
      ↓
Futura capa gobernada de entrega/presentación
```

## Fuera de alcance
- LLM o generación abierta.
- Selección de texto, voz, móvil, escritorio o automóvil.
- Síntesis de voz y prosodia.
- Envío o presentación de mensajes.
- Scheduling, timers o notificaciones.
- Herramientas, navegación o acciones externas.
- Mutación de memoria, relación o preferencias.
- Aprendizaje automático desde reacciones.

## Criterios de aceptación
- API pública desde `core.living_conversation`.
- Realizaciones inmutables, deterministas y persistibles.
- Preservación estricta de identidad, propietario y fuentes upstream.
- Abstención segura ante contenido no listo, preguntas incompletas o límites excedidos.
- Compatibilidad completa con M1–M98.
- Ruff limpio y suite completa sin regresiones.
