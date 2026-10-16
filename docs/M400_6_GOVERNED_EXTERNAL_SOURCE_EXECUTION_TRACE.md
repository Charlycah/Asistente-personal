# M400.6 — Governed External Source Execution Trace

## Propósito

M400.6 cierra la asimetría de trazabilidad detectada en M400.5 sin crear una
segunda autoridad de fuentes.

`GovernedSourceQueryExecutor`, cuya autoridad sigue siendo
`OfficialConversationGateway`, genera un `execution_id` SHA-256 al finalizar
cada consulta gobernada. El mismo identificador queda en el
`GovernedSourceQueryResult` y en su observación de ejecución.

**execution trace ≠ verdad certificada**

La identidad demuestra linaje técnico de una ejecución, no verdad semántica.

## Identidad de ejecución

El `execution_id` deriva del request de fuente, timestamps de ejecución y
recepción, estado terminal, items recibidos y error gobernado cuando existe.
Una consulta sólo preparada no tiene `execution_id`.

M400.6 no introduce un manager, repository o executor paralelo.

## Integración con M400

M400.4 conserva su admisión original `admit_query_result`, que permanece válida
para evidencia sin trace y por ello continúa siendo `LIMITED` bajo M400.5.

M400.6 añade de forma explícita `admit_traced_query_result`. Esta ruta exige un
`execution_id` real y lo incorpora a `ExternalIntelligenceProvenance.trace_ids`.

Así, una fuente correctamente ejecutada y admitida con trace puede alcanzar
`VERIFIED` en M400.5 por procedencia, sin cambiar `truth_certified=False`.

## Autoridad y límites

- `OfficialConversationGateway` conserva la autoridad de consulta de fuentes.
- `GovernedSourceQueryExecutor` sigue siendo el único executor canónico.
- NASA no adquiere autoridad cognitiva.
- M400.6 no agrega polling, background, fetch automático ni nuevas fuentes.
- M400.6 no cambia la clasificación de fuentes.
- `VERIFIED` significa procedencia trazada, no contenido verdadero.
- **procedencia verificable ≠ verdad certificada**.
- **capacidad/evidencia externa ≠ autoridad cognitiva**.
