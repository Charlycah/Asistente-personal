# ROBY XI.2 — CAP-11 — RED contractual long-horizon E(N) → existing Reasoning re-entry

Estado: **RED CONTRACTUAL — sin modificación de producción**.

Baseline oficial de entrada: **13.718 PASS + Ruff limpio**.

## Objetivo

Congelar el contrato long-horizon que debe conectar un E(N) ya adquirido con el owner canónico existente de Reasoning, sin crear una segunda autoridad y sin continuar todavía hacia R(N+1).

Frontera contractual:

`E3 → RR3` y `E4 → RR4`, preservando `E2 → RR2` histórico y **STOP antes de R(N+1)**.

## Autoridades preservadas

El contrato exige reutilizar exactamente:

- `GovernedMultiStepInvestigationReasoningClosureV1` como owner canónico de cierre/reentrada de Reasoning;
- `GovernedLevel2ReasoningReentryFoundationV1` como autoridad de reentrada de Reasoning;
- `GovernedMultiStepInvestigationEpisodeBoundaryV1` como autoridad de estado/budget/stopping del Episode.

No se introduce ningún owner, manager, loop, planner, authorization gateway ni execution gateway nuevo.

## RED E3 → RR3

Para un E3 long-horizon canónico con budget máximo 4:

- el bridge debe llamar al owner canónico de Reasoning exactamente una vez;
- debe reenviar por identidad el `execution_reentry` E3;
- Reasoning debe ejecutarse exactamente una vez sobre el mismo evidence envelope;
- el closure canónico debe ser `RECORDED`;
- el Episode debe quedar `AWAITING_REQUIREMENT`;
- `current_step == 3`;
- `remaining_acquisitions == 1`;
- stopping reason `NONE`;
- el Episode no debe quedar cerrado;
- deben preservarse episode/execution/authorization/requirement/plan/source/world lineage;
- el bridge no debe crear R4 ni invocar Planning, Authorization o Execution.

## RED E4 → RR4

Para un E4 long-horizon canónico con budget máximo 4:

- el bridge debe llamar al mismo owner de Reasoning exactamente una vez;
- debe reenviar por identidad el `execution_reentry` E4;
- Reasoning debe ejecutarse exactamente una vez;
- el closure canónico debe ser `CLOSED`;
- el Episode debe quedar `CLOSED`;
- `current_step == 4`;
- `remaining_acquisitions == 0`;
- stopping reason `BUDGET_EXHAUSTED`;
- deben preservarse todos los identificadores y lineage;
- el bridge no debe crear R5 ni iniciar otra capacidad.

## Guardia histórica E2 → RR2

El contrato conserva explícitamente el recorrido ya certificado:

`E2 (budget 2) → RR2 → CLOSED / BUDGET_EXHAUSTED`.

Esto debe seguir verde durante RED y GREEN.

## STOP antes de R(N+1)

El resultado del bridge no puede:

- crear un requirement nuevo;
- exponer Planning/Authorization/Execution;
- reentrar Reasoning de nuevo;
- invocar curiosity;
- habilitar retry;
- modificar Memory o World Model;
- emitir conversación;
- iniciar procesos de background.

Este bloque termina después de registrar RR(N). La admisión/discriminación de R(N+1) pertenece al bloque siguiente.

## Resultado RED esperado

El bridge histórico `GovernedLongHorizonInvestigationRR2TerminalClosureV1` conserva guards rígidos de step 2/terminalidad. Por ello el fallo esperado para E3 y E4 ocurre **antes** de invocar `GovernedMultiStepInvestigationReasoningClosureV1`:

`expected spy.calls == 1; actual 0`.

Todo el resto de los guards históricos y del owner canónico N-step debe permanecer verde.

## Superficie productiva

**Ningún archivo productivo se modifica en RED.**

El único archivo productivo candidato para un futuro GREEN, si este RED queda certificado, es:

`app/governed_long_horizon_investigation_rr2_terminal_closure.py`

`.roby/config.json` permanece protegido e intacto.
