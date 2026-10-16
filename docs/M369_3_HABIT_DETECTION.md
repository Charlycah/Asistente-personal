# M369.3 — Habit Detection

## Propósito

M369.3 incorpora una evaluación gobernada y de solo lectura de repetición
conductual sobre preferencias candidatas revisables de M369.2.

```text
habit_detection
└── preference_learning
    └── learning_foundation
        └── cognitive_memory
```

## Historia temporal

`habit_detection` consume únicamente ocurrencias explícitas derivadas de
preferencias en estado `review_required`. Cada ocurrencia conserva identidad,
sujeto, comportamiento, fecha observada y confianza.

Una historia corta o concentrada en un único día produce
`insufficient_history`. Tres o más ocurrencias compatibles, distribuidas en al
menos tres días y con una extensión mínima de dos días, producen
`review_required`.

La identidad del candidato es determinista y la confianza es el promedio
explícito de las ocurrencias admitidas.

## Límites

M369.3 no acepta hábitos automáticamente, no modifica preferencias, no reconoce
patrones complejos, no adapta razonamiento, no autoriza persistencia y no
cambia el runtime.

## Invariantes

- Existe una única autoridad `habit_detection`.
- Toda ocurrencia proviene de una preferencia candidata revisable.
- Las ocurrencias son únicas y consistentes en sujeto y comportamiento.
- Repetición sin distribución temporal permanece como historia insuficiente.
- Todo candidato con historia suficiente continúa requiriendo revisión.
- Ningún resultado queda aceptado ni autorizado para persistencia.

## Criterio de aceptación

M369.3 se considera válida con Ruff limpio, suite completa sin regresiones,
documentación sincronizada y baseline M361 actualizado.
