# M391.7 — Predicción Gobernada

## Objetivo

Madurar la predicción introducida en M391.4 sin crear una nueva autoridad ni un
predictor paralelo. M391.7 consume exclusivamente un
`GovernedCausalPredictionReport` explícito y permite declarar predicciones con
identificador, horizonte y condiciones trazables.

## Autoridad

La autoridad canónica continúa siendo `governed_reasoning`.
`GovernedPredictionEvaluator` es un evaluador puro subordinado y no expone
`authority_id`.

## Contratos

- `GovernedPredictionRequest` declara la relación fuente, el horizonte y las
  condiciones explícitas.
- `GovernedPredictionAssessment` conserva la salida como `INFERENCE` y puede
  quedar condicionalmente soportada, contradicha, no resuelta o en revisión.
- `GovernedPredictionReport` conserva evidencia, riesgos y huella determinista
  del análisis fuente M391.4.

## Límites

M391.7 no transforma una predicción en hecho futuro. No calibra probabilidad,
no inventa porcentajes de confianza, no usa reloj interno y no verifica por sí
mismo que un resultado futuro haya ocurrido. Tampoco persiste, aprende,
modifica el modelo del mundo, planifica, decide ni ejecuta acciones.

La ausencia de una relación fuente exige revisión y la evidencia no resuelta
permanece explícitamente insuficiente. Los conflictos del análisis M391.4 se
propagan sin ser reparados silenciosamente.
