# M369.5 — Adaptive Reasoning

## Propósito

M369.5 incorpora `adaptive_reasoning` como autoridad gobernada y subordinada a
`pattern_recognition`. Su responsabilidad es producir sugerencias adaptativas
de solo lectura a partir de patrones revisables y opciones explícitamente
acotadas.

## Contrato

La autoridad recibe un contexto con sujeto, opciones disponibles y opción por
defecto. Solo considera evidencia procedente de patrones en `review_required`.
Cuando existe una coincidencia inequívoca, devuelve una sugerencia también en
`review_required`. Si no existe aprendizaje aplicable, devuelve
`no_applicable_learning` y conserva la opción por defecto.

## Gobierno

La sugerencia es únicamente consultiva. M369.5 no aplica adaptaciones automáticamente, no modifica objetivos ni políticas, no persiste aprendizaje y
no cambia el runtime. Toda aplicación efectiva queda reservada a capas futuras
y a políticas explícitas.
