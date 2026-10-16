# M326.5 — Decision Policy Engine

## Objetivo

Añadir una capa determinista que compare `ActionCandidate` y `RiskAssessment`
contra una `DecisionPolicy` y produzca una `AutonomyDecision` auditable, sin
autorizar ni ejecutar acciones.

## Incorporado

- `core/controlled_autonomy/decision_policy.py`
- `CandidatePolicyScore`
- `PolicyEvaluationStatus`
- `PolicyEvaluationResult`
- `DecisionPolicyEngine`
- `DeterministicDecisionPolicyEngine`

## Reglas principales

- Requiere exactamente una evaluación por candidato.
- Descarta candidatos prohibidos, con riesgo prohibido o bajo confianza mínima.
- Puntúa confianza, impacto, riesgo, reversibilidad y costo estimado.
- Conserva el orden original como desempate determinista.
- El modo simulación produce `SIMULATE`.
- `OBSERVE_ONLY` produce `OBSERVE` cuando no hay simulación.
- Las políticas operativas producen `RECOMMEND` cuando no hay simulación.
- Si no existe ningún candidato elegible, produce `BLOCK`.
- Nunca produce `AUTHORIZE` ni `REQUEST_CONFIRMATION`; esas decisiones quedan
  reservadas para M326.6 — Autonomy Gate.

## Seguridad

No se añadieron ejecutores, llamadas a herramientas, cambios de runtime,
confirmaciones ni efectos secundarios.

## Pruebas

- 33 pruebas nuevas en `tests/test_m326_5_decision_policy_engine.py`.
- Suite completa en este entorno: 7535 pruebas aprobadas.
