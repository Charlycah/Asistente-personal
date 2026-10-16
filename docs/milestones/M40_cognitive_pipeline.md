# M40 - Cognitive Pipeline

## Estado

Ready for local validation.

## Objetivo

Integrar las capas cognitivas construidas entre M33 y M39 en un único pipeline
orquestado y testeable.

El pipeline une:

1. Cognitive Intent Analyzer (M33)
2. Conversation Strategy (M34)
3. Cognitive Learning Policy (M35)
4. Cognitive Memory Store (M36)
5. Cognitive Memory Recall (M37)
6. Cognitive Memory Integration (M38)
7. Memory-aware Prompt Context (M39)
8. LLM Service (M31), opcional e inyectado

## Alcance

M40 no agrega una nueva política cognitiva, no cambia proveedores, no introduce
embeddings y no activa comportamiento proactivo. Su responsabilidad es conectar
lo existente en un flujo único.

## Flujo

```text
Usuario
  -> CognitiveMemoryIntegration
  -> MemoryPromptContextBuilder
  -> final prompt
  -> LLMService
  -> LLMResponse
```

## Decisiones

- El LLM sigue siendo opcional e inyectado.
- La memoria se recupera antes de construir el prompt.
- El system prompt se deriva de la estrategia conversacional.
- Las consultas domésticas pueden saltar el LLM si la estrategia así lo indica.
- No se acopla el pipeline a Ollama, Gemini ni Mistral.

## Validación esperada

```bash
ruff check .
pytest
```

El cierre requiere suite completa verde y Ruff limpio.
