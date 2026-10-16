# M38 — Cognitive Memory Integration

## Objetivo

Integrar las piezas cognitivas cerradas entre M33 y M37 en un único flujo
mínimo y testeable.

M38 conecta:

- `CognitiveIntentAnalyzer` (M33)
- `ConversationStrategyPlanner` (M34)
- `CognitiveLearningPolicy` (M35)
- `CognitiveMemoryStore` (M36)
- `CognitiveMemoryRecall` (M37)

## Alcance

El milestone introduce `CognitiveMemoryIntegration`, una capa de orquestación
que procesa un turno de conversación y devuelve un resultado estructurado con:

- intención cognitiva,
- estrategia conversacional,
- recuerdos recuperados,
- decisión de aprendizaje,
- ids de memorias persistidas.

## Fuera de alcance

M38 no hace prompt building, no llama al LLM, no usa embeddings, no modifica
proveedores y no genera comentarios proactivos.

La integración recupera memoria antes de guardar aprendizajes del turno actual.
Eso evita que ROBY use el mismo input recién escrito como recuerdo relevante.

## Criterios de aceptación

- El pipeline analiza intención y estrategia en un único flujo.
- Puede recuperar recuerdos existentes desde SQLite.
- Puede almacenar aprendizajes aprobados por la política cognitiva.
- Permite desactivar recall o aprendizaje por turno.
- No acopla la memoria cognitiva al `AgentLoop` todavía.
- Tests específicos verdes.
- Suite completa verde.
- Ruff limpio.

## Resultado

ROBY ya puede ejecutar el primer ciclo interno de su cerebro:

```text
texto
  ↓
intent analyzer
  ↓
conversation strategy
  ↓
memory recall
  ↓
learning policy
  ↓
memory store
```

Este flujo prepara M39, donde los recuerdos recuperados podrán convertirse en
contexto útil para construir prompts cognitivos antes de llamar al LLM.
