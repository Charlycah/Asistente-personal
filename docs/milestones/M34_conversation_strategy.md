# M34 — Conversation Strategy

## Objetivo

Introducir la segunda pieza de la capa cognitiva de ROBY: una estrategia de
conversación derivada del resultado de `CognitiveIntentAnalyzer`.

M33 responde qué tipo de conversación está teniendo ROBY. M34 responde cómo debe
abordarla: tono, profundidad, formato, uso de LLM y necesidad de aclaración.

## Alcance

Incluido:

- `ConversationStrategyPlanner`.
- `ConversationStrategy` inmutable.
- Tonos conversacionales mínimos.
- Profundidad recomendada.
- Formato de respuesta sugerido.
- Señales de uso de LLM y aclaración.
- Tests específicos para cada intención cognitiva.

Excluido:

- Memoria.
- Proactividad.
- Herramientas.
- Selección automática de proveedor.
- Cambios en adaptadores Ollama, Gemini o Mistral.
- Cambios en UI o voz.

## Diseño

Flujo conceptual:

```text
User text
   ↓
CognitiveIntentAnalyzer  (M33)
   ↓
CognitiveIntentResult
   ↓
ConversationStrategyPlanner  (M34)
   ↓
ConversationStrategy
```

La estrategia contiene:

- `tone`
- `depth`
- `response_format`
- `should_use_llm`
- `should_ask_clarifying_question`
- `system_hints`
- `metadata`

## Decisiones

- La estrategia es determinística y testeable.
- No hay llamadas a red.
- No se introduce memoria todavía.
- No se modifica el contrato LLM.
- Las preguntas domésticas permanecen fuera del LLM cuando M33 así lo indica.
- Las intenciones desconocidas generan una estrategia de aclaración.

## Criterios de cierre

- Tests específicos de M34 en verde.
- Suite completa en verde.
- Ruff limpio.
- Sin regresiones en M27–M33.
