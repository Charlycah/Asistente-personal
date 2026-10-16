# RP.20.23 — Campos canónicos en resultados cognitivos

Se retiraron propiedades públicas que sólo extraían un campo ya disponible en un resultado anidado:

- `CognitivePipelineResult.intent`
- `CognitivePipelineResult.used_memory`
- `CognitivePipelineResult.learned_something`
- `CognitiveMemoryIntegrationResult.used_memory`

Las consultas canónicas son ahora explícitas:

- `result.memory_result.intent_result.intent.value`
- `result.prompt_context.should_include`
- `result.memory_result.learned_something`
- `result.recall_result.should_use_memory`

Se preservaron las propiedades que sí derivan una condición: `CognitivePipelineResult.called_llm` y `CognitiveMemoryIntegrationResult.learned_something`.
