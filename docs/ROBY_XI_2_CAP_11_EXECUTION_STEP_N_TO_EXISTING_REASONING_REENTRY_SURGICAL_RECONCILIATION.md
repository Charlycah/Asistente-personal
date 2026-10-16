# CAP-11 — Execution ACQUIRED step N → existing Reasoning re-entry
## Reconciliación quirúrgica

Baseline de entrada: 13.702 PASS + Ruff limpio, certificada localmente.

## Autoridades canónicas existentes

Reasoning re-entry:
`GovernedLevel2ReasoningReentryFoundationV1`

Owner de integración Reasoning + Episode:
`GovernedMultiStepInvestigationReasoningClosureV1`

Episode / budget / stopping:
`GovernedMultiStepInvestigationEpisodeBoundaryV1.record_reentry(...)`

No hace falta un segundo Reasoning owner, un nuevo Episode owner, un loop ni un
scheduler.

## Residual real

`GovernedMultiStepInvestigationReasoningClosureV1` sigue codificado como cierre
terminal RR2. El bloqueo no está en el Reasoning foundation ni en Episode.

Supuestos terminales actuales:
- exige `current_step == 2`;
- exige `remaining_acquisitions == 0`;
- exige `consumed_acquisitions == max_acquisitions`;
- después de `record_reentry(...)` sólo acepta `STOP_REQUIRED`;
- exige estado `CLOSED`;
- exige `BUDGET_EXHAUSTED`;
- su resultado sólo modela `CLOSED`, `NOT_ELIGIBLE` y `REVIEW_REQUIRED`;
- las invariantes del resultado prohíben un re-entry intermedio válido.

## Invariante N-step de entrada

Un Execution result puede entrar al owner existente sólo cuando:
- status `ACQUIRED`;
- `eligible_for_reasoning_reentry=True`;
- exactamente una invocación de Execution;
- exactamente un registro de adquisición;
- evidence envelope presente;
- Episode en `AWAITING_REENTRY`;
- `2 <= current_step <= max_acquisitions`;
- `consumed_acquisitions == current_step`;
- `remaining_acquisitions == max_acquisitions - consumed_acquisitions`;
- lineage exacto execution/authorization/requirement/plan/source/snapshot;
- no reentry id reutilizado.

## Resultado intermedio

Si después de `record_reentry(...)` queda budget:
- decisión `CONTINUE_ALLOWED`;
- Episode `AWAITING_REQUIREMENT`;
- stopping reason `NONE`;
- remaining > 0;
- el resultado debe representar un re-entry registrado no terminal;
- no crea ni admite requirement;
- no invoca Planning, Authorization ni Execution;
- STOP.

## Resultado terminal

Si la adquisición consumió el budget:
- decisión `STOP_REQUIRED`;
- Episode `CLOSED`;
- stopping reason `BUDGET_EXHAUSTED`;
- remaining == 0;
- conserva exactamente el comportamiento histórico RR2 para budget 2 y permite
  el equivalente terminal RR4 para budget 4.

## Frontera STOP

Este bloque termina inmediatamente después del Reasoning re-entry existente y
`record_reentry(...)`.

No crea/admite R(N+1), no ejecuta discriminación para producir requirement, no
invoca Planning, Authorization, Execution, Curiosity, Memory, World Model,
conversation, background work ni retry.

## Cambio futuro mínimo

El RED deberá exigir RR3 intermedio (`AWAITING_REQUIREMENT`) y RR4 terminal,
preservar RR2 histórico y demostrar por source contract que no se introduce una
segunda autoridad.
