# M326.2 — Situation Assessment

Base estable: M326.1 (`ruff` OK, 7402 tests OK).

## Incorporado

- `RuntimeObservation`: hecho inmutable y trazable del runtime.
- `SituationRule`: regla determinista de normalización.
- `DeterministicSituationAssessor`: convierte observaciones elegibles en
  `DecisionSituation`.
- `SituationAssessmentResult`: distingue situación identificada, ausencia de
  situación y observación no soportada.
- Adaptadores puros para `ExecutiveEvent` y `ComponentHealth`.
- Reglas iniciales para batería baja, recordatorios y salud degradada o no sana.

## Límites

M326.2 no genera candidatos, no evalúa riesgos, no autoriza y no ejecuta
acciones. Su única responsabilidad es convertir evidencia existente en una
situación estructurada, explicable y auditable.
