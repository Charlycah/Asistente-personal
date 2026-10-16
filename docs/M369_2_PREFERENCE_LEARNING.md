# M369.2 — Preference Learning

## Propósito

M369.2 incorpora una evaluación gobernada y de solo lectura de evidencia de
preferencias sobre la fundación M369.1.

```text
preference_learning
└── learning_foundation
    └── cognitive_memory
```

## Evidencia y candidato

`preference_learning` consume únicamente candidatos trazables de M369.1. Toda
la evidencia debe respaldar un mismo sujeto y un mismo valor propuesto.

Una sola evidencia produce `insufficient_evidence`. Dos o más evidencias
consistentes producen `review_required`. En ambos casos el resultado sigue
siendo un candidato revisable.

La confianza se calcula como promedio explícito de la confianza aportada por
las evidencias y la identidad es determinista para entradas idénticas.

## Límites

M369.2 no convierte una observación aislada en preferencia, no acepta
preferencias automáticamente, no autoriza persistencia y no modifica perfiles.
Tampoco detecta hábitos, reconoce patrones, adapta razonamiento ni cambia el
runtime.

## Invariantes

- Existe una única autoridad `preference_learning`.
- Toda evidencia proviene de candidatos estructurados por M369.1.
- Las evidencias son únicas y consistentes en sujeto y valor.
- Una evidencia aislada permanece como evidencia insuficiente.
- Una preferencia candidata siempre requiere revisión antes de cualquier uso.
- Ningún resultado queda aceptado ni autorizado para persistencia.

## Criterio de aceptación

M369.2 se considera válida con Ruff limpio, suite completa sin regresiones,
documentación sincronizada y baseline M361 actualizado.
