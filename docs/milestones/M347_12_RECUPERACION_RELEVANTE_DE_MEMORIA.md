# M347.12 — Recuperación relevante de memoria

## Objetivo

Fortalecer el `CognitiveMemoryRecall` canónico para que la memoria recuperada sea
seleccionada mediante una decisión explícita, trazable y subordinada al mismo
contexto conversacional y a la misma estrategia cognitiva.

## Integración

M347.12 no crea otro recuperador, índice, store ni motor semántico. Extiende el
recall existente con `MemoryRelevanceDecision`, que registra de forma segura:

- si corresponde usar memoria;
- motivo de selección o descarte;
- cantidad de candidatos considerados, seleccionados y rechazados;
- umbral mínimo aplicado;
- uso del `ConversationContext` canónico;
- señales contextuales estructuradas.

El contexto aporta el tema activo, entidades, referencias pendientes y objetivo
de corrección. Estas señales enriquecen la búsqueda y el ranking dentro del
mismo `CognitiveMemoryRecall`.

## Reglas

- Solo se seleccionan recuerdos cuyo score alcanza el umbral explícito.
- Los recuerdos archivados nunca se proyectan al turno.
- La ausencia de candidatos o de relevancia produce un resultado vacío seguro.
- La recuperación no modifica el contexto ni decide la respuesta.
- La decisión serializable no incluye contenido de memoria, prompts ni
  razonamiento privado.
- Se preservan SQLite, la política de escritura y el pipeline de integración
  existentes.

## Fuera de alcance

M347.12 no incorpora embeddings, búsqueda externa, persistencia nueva,
deduplicación, reconciliación de correcciones, prompt building ni generación de
respuestas.
