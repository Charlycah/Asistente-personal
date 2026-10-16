# ADR-098 — Reflection Generation

## Estado
Aceptado para M96.

## Contexto
M93 gobierna la intervención, M94 detecta oportunidades y M95 recomienda la ventana temporal. Faltaba una frontera que transformara una oportunidad autorizada en contenido previo sin otorgar a la capa generativa autoridad para decidir, hablar o inventar hechos.

## Decisión
Crear `core.living_conversation.reflection` como compositor determinista de borradores estructurados. La generación exige una decisión M93 `intervene`, una decisión M95 `intervene_now`, un `content_hint` y, salvo respuestas explícitas, referencias de fuente.

El resultado es inmutable, trazable y puede ser `generated`, `abstained` o `review_required`. Contiene forma, tono, apertura, puntos, pregunta de cierre, fuentes y razones.

## Consecuencias
- La composición queda separada de gobernanza, timing, LLM y entrega.
- La ausencia de evidencia produce abstención, no invención.
- Los contextos y oportunidades de M93/M95 deben coincidir.
- Un milestone posterior podrá enriquecer el lenguaje manteniendo este contrato como frontera de seguridad.
