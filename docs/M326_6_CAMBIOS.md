# ROBY XI.2 M326.6 — Autonomy Gate

## Objetivo

Agregar una compuerta determinista que transforme una decisión de política en
una disposición gobernada, sin ejecutar acciones.

## Incorporado

- `AutonomyGate`
- `DeterministicAutonomyGate`
- `AutonomyGateResult`
- `GateEvaluationStatus`

## Reglas

- simulación siempre prevalece;
- acciones o riesgos prohibidos se bloquean;
- `observe_only` solo observa;
- `recommend` solo recomienda;
- `confirm_before_action` solicita confirmación;
- `autonomous_low_risk` solo autoriza riesgo bajo, confianza suficiente y
  reversibilidad compatible con la política;
- cualquier incumplimiento de autorización automática solicita confirmación;
- no existe ejecución de acciones en M326.6.
