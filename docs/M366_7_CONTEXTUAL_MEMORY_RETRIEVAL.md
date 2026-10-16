# M366.7 — Contextual Memory Retrieval

M366.7 declara una política transversal, gobernada y de sólo lectura para seleccionar recuerdos relevantes según el contexto actual.

La implementación histórica `core.cognitive_memory_recall:CognitiveMemoryRecall` permanece como mecanismo especializado de recuperación. La autoridad canónica continúa siendo `memory_gateway`.

La selección puede considerar coincidencia contextual, confianza, vigencia, confirmación del usuario y versiones corregidas. Los recuerdos archivados o reemplazados se excluyen, mientras que las contradicciones se derivan a revisión.

El contenido seleccionado no se inyecta automáticamente en prompts ni altera respuestas. M366.7 no persiste, no consolida, no aprende y no modifica el runtime conversacional.
