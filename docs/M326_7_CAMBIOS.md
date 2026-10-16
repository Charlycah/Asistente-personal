# ROBY XI.2 M326.7 — Outcome Supervisor

## Objetivo

Agregar una capa determinista que evalúe el resultado observado de una acción
autorizada y produzca una directiva de seguimiento auditable, sin ejecutar la
recuperación.

## Incorporado

- `OutcomeSupervisor`
- `DeterministicOutcomeSupervisor`
- `OutcomeSupervisionResult`
- `OutcomeSupervisionStatus`
- `OutcomeDirective`

## Directivas

- `none`
- `complete`
- `retry`
- `revert`
- `degrade`

La necesidad de notificar al usuario se representa por separado mediante
`notify_user`.

## Reglas principales

- una acción exitosa completa el ciclo;
- un fallo reintenta mientras exista presupuesto de intentos;
- agotados los intentos, una acción reversible solicita reversión;
- una acción irreversible fallida solicita degradación controlada;
- estados revertidos, degradados o desconocidos pueden exigir notificación;
- decisiones no autorizadas se consideran no aplicables;
- no existen métodos de ejecución, reintento, reversión o notificación.

## Validación

- 30 pruebas nuevas;
- 7594 pruebas totales;
- compilación Python correcta;
- líneas limitadas a 88 caracteres.
