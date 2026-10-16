# M58 — Confianza y Explicabilidad

## Propósito

M58 agrega una capa de convivencia orientada a calibrar confianza, explicar
límites y sostener trazabilidad en respuestas prolongadas. No reemplaza el
ciclo cognitivo ni las capas M51-M57: consume sus señales para decidir cómo
hacer más clara, verificable y honesta una interacción.

## Alcance

- Detectar solicitudes de explicación, validación, trazabilidad, confiabilidad e
  incertidumbre.
- Calibrar una postura operativa: `baseline`, `explain`, `verify`, `calibrate`
  o `audit`.
- Generar guías de explicación y notas de incertidumbre sin inventar hechos.
- Asociar snapshots previos de relación, iniciativa, regulación social,
  personalidad y colaboración.
- Exponer líneas de `system_prompt` para guiar respuestas posteriores.

## Componentes

- `core/trust_explainability.py`
  - `TrustSignal`
  - `TrustPosture`
  - `TrustExplainabilityPolicy`
  - `TrustExplainabilitySnapshot`
  - `TrustExplainabilityEngine`
  - `TrustExplainabilityManager`

## Integración

`CognitivePipeline` acepta opcionalmente `trust_explainability`. Si está
presente, M58 observa el turno después de M57 y antes de construir el prompt
final. La integración es no destructiva y todos los parámetros son opcionales.

## Garantías

- Sin ejecución en segundo plano.
- Sin prometer validaciones no realizadas.
- Sin reemplazar módulos previos.
- Sin romper contratos públicos existentes.
- Snapshots inmutables y serializables.

## Validación

Pruebas agregadas:

- `tests/test_m58_trust_explainability.py`

Validación local realizada:

- M58 específico: 8 tests en verde.
- M50-M58: 72 tests en verde.
- Suite completa: 628 tests en verde.
