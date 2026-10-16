# ROBY XI.2 M326.4 — Risk & Confidence Evaluator

M326.4 agrega una evaluación determinista y sin efectos secundarios de cada
`ActionCandidate` producido por M326.3.

## Incorporado

- `RiskProfile`
- `RiskEvaluationStatus`
- `RiskEvaluationResult`
- `RiskConfidenceEvaluator`
- `DeterministicRiskConfidenceEvaluator`
- `default_risk_profiles()`

## Garantías

- perfiles explícitos por acción;
- confianza e impacto acotados entre 0.0 y 1.0;
- escalamiento conservador por irreversibilidad e impacto alto;
- trazabilidad completa hacia perfil, situación y candidato;
- resultado explícito para candidatos vacíos o acciones sin perfil;
- ningún método de decisión, autorización o ejecución.
