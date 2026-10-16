# ADR-089 — Meta-Reasoning

## Estado

Aceptado para M87.

## Decisión

Introducir una capa posterior al razonamiento gobernado que evalúe la calidad del
proceso mediante assessments inmutables, hallazgos dimensionados y
recomendaciones consultivas.

M87 no modifica el resultado de M84, no repite inferencias, no altera modelos
mentales y no ejecuta recomendaciones.

## Consecuencias

- La calidad del razonamiento queda observable y trazable.
- Incertidumbre, conflictos, evidencia, explicación y alcance se evalúan de forma
  explícita.
- M88 podrá reflexionar sobre assessments persistidos sin mezclar reflexión con
  la evaluación inmediata del proceso.
