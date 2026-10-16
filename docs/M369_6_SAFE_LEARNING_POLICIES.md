# M369.6 — Safe Learning Policies

## Propósito

M369.6 incorpora `safe_learning_policies` como autoridad canónica subordinada a
`adaptive_reasoning`. Su responsabilidad es aplicar reglas deterministas de
seguridad a candidatos de aprendizaje antes de cualquier revisión humana.

## Decisiones gobernadas

La política puede clasificar un candidato como:

- `insufficient_evidence`;
- `review_required`;
- `rejected`;
- `expired`.

La evaluación considera evidencia mínima, confianza, antigüedad,
contradicciones y consentimiento explícito para aprendizaje sensible.

## Límites

M369.6 no acepta aprendizajes automáticamente, no autoriza persistencia, no
aplica adaptaciones, no cambia objetivos o políticas y no modifica el runtime.
Incluso un candidato que supera todas las reglas permanece en
`review_required`.
