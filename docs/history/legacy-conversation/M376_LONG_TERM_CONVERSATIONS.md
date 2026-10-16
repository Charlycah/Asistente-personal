# M376 — Conversaciones de Largo Plazo

## Propósito

M376 permite cerrar y recuperar una conversación mediante un registro resumido,
gobernado y explícito. No convierte el historial bruto en memoria ni duplica la
autoridad de Memoria Cognitiva.

## Autoridad canónica

`LongTermConversationAuthority` es la única autoridad para archivar y recuperar
registros conversacionales resumidos. Trabaja mediante
`LongTermConversationRepository`; M376 incluye solamente un repositorio en
memoria para validar el contrato sin conectar persistencia de producción.

## Registro canónico

`LongTermConversationRecord` conserva identificador, resumen explícito, período,
tema, entidades, preguntas pendientes y cantidad de turnos de origen. El registro
es sensible por defecto y prohíbe retener el transcript completo.

## Límites

M376 no incorpora resumen automático, LLM, búsqueda semántica, RAG, historial
completo, persistencia en disco, integración al runtime, escritura en
`OfficialMemoryGateway`, aprendizaje ni personalidad adaptativa.

## Invariantes

1. Una sola autoridad archiva y recupera conversaciones.
2. El resumen debe ser suministrado explícitamente.
3. El transcript bruto no se conserva.
4. El archivo conversacional no es memoria cognitiva.
5. La conexión persistente y la recuperación semántica requieren hitos futuros.
