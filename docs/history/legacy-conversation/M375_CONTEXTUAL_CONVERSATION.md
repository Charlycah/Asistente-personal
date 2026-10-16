# M375 — Conversación Contextual

## Propósito

M375 inicia la Fase III para que ROBY mantenga continuidad entre turnos mediante un estado conversacional gobernado, en lugar de depender únicamente del último mensaje o de un historial bruto.

## Autoridad canónica

`ConversationContextAuthority` es la única autoridad para consultar, actualizar y cerrar el contexto conversacional inmediato. Reutiliza `ConversationContext`; no crea un segundo modelo mental ni una memoria paralela.

## Contratos

- `ConversationTurn`: hecho inmutable de un turno observado.
- `ConversationReferenceResolution`: resultado explícito de una referencia básica.
- `ConversationContextUpdate`: transición trazable entre contexto anterior y actual.
- `ConversationContextAuthority`: autoridad en memoria, aislada por `conversation_id`.

## Continuidad básica

La autoridad conserva tema activo, entidades, intención cognitiva, intención de interacción, acción previa y número de turno. Las entidades nuevas se incorporan sin duplicados. Referencias simples como `su`, `sus`, `él`, `ella`, `ese proyecto` o `el anterior` se resuelven únicamente contra una entidad activa explícita. Si no existe una entidad disponible, la referencia queda pendiente.

## Límites

M375 no incorpora:

- persistencia ni historial completo;
- memoria de largo plazo;
- recuperación semántica o RAG;
- llamadas a LLM;
- inferencia libre de entidades;
- personalidad adaptativa;
- resumen automático;
- planificación conversacional avanzada;
- cambios en el runtime oficial.

## Invariantes

1. Una sola autoridad modifica el contexto.
2. Los turnos son hechos; el contexto es estado derivado.
3. Las conversaciones permanecen aisladas por identificador.
4. La resolución es determinista y auditable.
5. Cerrar una conversación elimina únicamente su estado inmediato en memoria.
