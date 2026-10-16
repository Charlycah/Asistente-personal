# M39 — Memory-aware Prompt Context

## Objetivo

Transformar recuerdos recuperados por la memoria cognitiva en un bloque de
contexto compacto y seguro para enriquecer prompts futuros.

## Alcance

M39 agrega una capa de construcción de contexto sobre M37/M38. No llama al LLM,
no consulta SQLite directamente, no ejecuta proveedores y no introduce
proactividad. Su responsabilidad es tomar un resultado de recall y convertirlo
en texto estructurado que pueda ser usado por milestones posteriores.

## Cambio mínimo

- `core/memory_prompt_context.py`
- `tests/test_m39_memory_prompt_context.py`

## Decisiones

- El contexto se construye solo si el recall indica memoria relevante.
- Se limita la cantidad de recuerdos incluidos.
- Cada recuerdo se compacta para evitar prompts demasiado largos.
- La estrategia conversacional puede adjuntarse como metadato textual.
- El builder puede envolver el prompt del usuario, pero no llama al modelo.

## Fuera de alcance

- Embeddings.
- Vector DB.
- Prompt final del agente.
- Integración directa con `LLMService`.
- Comentarios proactivos.
- Compactación o pruning de memoria.

## Criterios de cierre

- Tests específicos de M39 en verde.
- Suite completa en verde.
- Ruff limpio.
- Sin regresiones en milestones previos.
