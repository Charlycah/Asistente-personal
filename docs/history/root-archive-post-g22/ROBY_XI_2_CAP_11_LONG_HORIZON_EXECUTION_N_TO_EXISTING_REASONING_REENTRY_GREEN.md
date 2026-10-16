# ROBY XI.2 — CAP-11 — Long-horizon E(N) → existing Reasoning re-entry RR(N) — GREEN

Estado: **GREEN quirúrgico listo para certificación local**.

Baseline de entrada certificada por el usuario: **13.718 PASS + Ruff limpio**.

## Alcance

Se generalizó exclusivamente el bridge histórico:

`app/governed_long_horizon_investigation_rr2_terminal_closure.py`

Clase pública histórica preservada:

`GovernedLongHorizonInvestigationRR2TerminalClosureV1`

No se creó ni modificó otra autoridad de Reasoning, Episode, Planning, Authorization o Execution.

## Autoridad canónica preservada

El único owner utilizado continúa siendo:

`GovernedMultiStepInvestigationReasoningClosureV1`

El bridge reenvía por identidad el `execution_reentry` ya producido por E(N) y lo invoca exactamente una vez.

## Generalización implementada

El bridge histórico ya no exige step 2 ni budget terminal cero para admitir E(N). Ahora exige alineación exacta entre:

- `execution_reentry.current_step` y `state.current_step`;
- `execution_reentry.remaining_acquisitions` y `state.remaining_acquisitions`;
- `state.consumed_acquisitions == state.current_step`;
- `state.remaining_acquisitions == state.max_acquisitions - state.current_step`;
- lineage exacto de episode/execution/authorization/requirement/plan/source/world;
- Execution adquirido, registrado una vez y reasoning-eligible.

## RR(N) intermedio

Cuando el owner canónico devuelve `GovernedInvestigationReasoningClosureStatus.RECORDED`, el bridge conserva ese producto exactamente y expone el status histórico ampliado `RECORDED`.

Para E3 con budget 4 el contrato exige:

- RR3 `RECORDED`;
- Episode `AWAITING_REQUIREMENT`;
- `current_step == 3`;
- `remaining_acquisitions == 1`;
- stopping reason `NONE`;
- Episode no cerrado.

## RR(N) terminal

Cuando el owner canónico devuelve `CLOSED`, el bridge conserva el cierre terminal.

Para E4 con budget 4 el contrato exige:

- RR4 `CLOSED`;
- Episode `CLOSED`;
- remaining 0;
- `BUDGET_EXHAUSTED`;
- Episode cerrado.

## Compatibilidad histórica

E2 con budget 2 continúa produciendo RR2 terminal `CLOSED / BUDGET_EXHAUSTED`. Los nombres públicos RR2 se preservan para evitar una migración API innecesaria.

## STOP gobernado

El bridge no crea ni admite R(N+1), no invoca Planning, Authorization ni Execution, no ejecuta Curiosity, no modifica memoria/world model y no inicia procesos de fondo. El frontier termina en RR(N).

## Validación del entorno del asistente

- contrato nuevo E3→RR3 / E4→RR4 + guards relacionados: **28 passed**;
- batería relacionada ampliada: **54 passed**;
- `python -m compileall -q app core tests`: limpio;
- chequeo manual de líneas > 88 en archivos afectados: 0;
- Ruff no está instalado en el contenedor del asistente, por lo que la certificación oficial requiere ejecución local del usuario.

## Certificación requerida

```bash
ruff check .
pytest -q
```

La baseline oficial sólo debe actualizarse con el resultado real de esa ejecución local.
