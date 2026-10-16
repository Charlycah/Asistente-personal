# M37 — Cognitive Memory Recall

## Objetivo

Agregar una capa mínima de recuperación cognitiva para que ROBY pueda consultar
la DB cerebral creada en M36 cuando una conversación lo justifique.

## Alcance

M37 recupera recuerdos estructurados desde SQLite usando señales determinísticas:

- texto normalizado del turno,
- intención cognitiva de M33,
- estrategia conversacional de M34,
- categoría del aprendizaje,
- tags y confianza del recuerdo.

## Fuera de alcance

M37 no introduce:

- embeddings,
- vector DB,
- llamadas al LLM,
- comentarios proactivos,
- compactación de memoria,
- cambios en proveedores de modelos,
- cambios en UI o voz.

## Diseño

La nueva capa se ubica encima de `CognitiveMemoryStore`:

```text
Conversation turn
      ↓
CognitiveIntentResult
      ↓
ConversationStrategy
      ↓
CognitiveMemoryRecall
      ↓
CognitiveMemoryStore
      ↓
Relevant memories
```

## Componentes

- `CognitiveMemoryRecallRequest`: entrada del recall.
- `CognitiveMemoryRecallItem`: recuerdo recuperado con score y señales.
- `CognitiveMemoryRecallResult`: resultado final de recuperación.
- `CognitiveMemoryRecall`: servicio de consulta cognitiva.

## Criterios de aceptación

- Recupera recuerdos por coincidencia textual.
- Recupera recuerdos por intención/tag.
- Prioriza recuerdos por score, confianza y señales compartidas.
- Respeta límites de resultados.
- Marca recuerdos como accedidos mediante el store de M36.
- Devuelve resultado seguro cuando no hay señales útiles.
- No depende de red, LLM ni embeddings.
- Mantiene Ruff limpio y suite completa verde.
