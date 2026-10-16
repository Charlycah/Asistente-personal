# M36 — Cognitive Memory Store

## Estado

CLOSED cuando Ruff y la suite completa pasan localmente.

## Objetivo

Persistir los aprendizajes aprobados por `CognitiveLearningPolicy` en una base
local estructurada y consultable. Este milestone crea la primera DB cerebral de
ROBY sin introducir recuperación semántica, embeddings ni comportamiento
proactivo.

## Decisión de diseño

M36 usa SQLite como store inicial porque ROBY todavía es local, monousuario y
necesita una base portable, simple de testear y fácil de versionar. SQLite es
suficiente para esta etapa si los recuerdos se guardan como conocimiento
estructurado, no como transcripciones infinitas.

La DB incluye:

- tabla de versión de esquema;
- tabla `cognitive_memories`;
- índices por categoría y fecha;
- contenido normalizado;
- tags y metadata en JSON;
- conteo de accesos para futuros algoritmos de recall o compactación.

## Fuera de alcance

- Vector DB.
- Embeddings.
- Recuperación semántica.
- Compactación automática.
- Políticas de olvido.
- Comentarios proactivos.
- Cambios en memoria persistente previa.

## Cambio mínimo

- `core/cognitive_memory_store.py`
- `tests/test_m36_cognitive_memory_store.py`

## Criterios de aceptación

- El store inicializa el esquema SQLite.
- Solo persiste candidatos con acción `STORE`.
- Permite recuperar recuerdos por ID.
- Permite búsquedas simples por texto, categoría y tag.
- Conserva metadata y tags.
- Registra conteo de accesos.
- Persiste entre instancias.
- No depende de red ni de proveedores LLM.
- Ruff limpio.
- Suite completa en verde.

## Nota sobre crecimiento

ROBY no debe almacenar todo sin parar. M36 solo crea el store. La política de
retención, resumen, compactación y migración futura queda reservada para
milestones posteriores. El camino recomendado es:

1. SQLite local estructurado.
2. Compactación y pruning.
3. Búsqueda semántica opcional con embeddings.
4. Migración a vector store o base híbrida si el volumen lo exige.
