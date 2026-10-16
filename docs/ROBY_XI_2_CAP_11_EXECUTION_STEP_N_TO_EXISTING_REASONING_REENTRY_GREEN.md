# CAP-11 — Execution step N → existing Reasoning re-entry — GREEN

Estado: GREEN quirúrgico pendiente de certificación local completa.

## Producción

Se generalizó exclusivamente
`GovernedMultiStepInvestigationReasoningClosureV1`.

Se preservan las autoridades existentes:
- Reasoning: `GovernedLevel2ReasoningReentryFoundationV1`;
- Episode / budget / stopping:
  `GovernedMultiStepInvestigationEpisodeBoundaryV1.record_reentry(...)`.

No se creó un segundo Reasoning owner, planner, authorization owner, executor,
manager, loop ni scheduler.

## Admisión N-step

Un Execution result entra sólo si:
- status `ACQUIRED`;
- `eligible_for_reasoning_reentry=True`;
- una sola invocación de Execution;
- un solo registro de adquisición;
- Episode `AWAITING_REENTRY`;
- `2 <= current_step <= max_acquisitions`;
- `state.current_step == current_step`;
- `consumed_acquisitions == current_step`;
- el budget restante del resultado coincide con el Episode.

## Re-entry intermedio

Si queda budget después de E(N):
- se invoca exactamente una vez el Reasoning re-entry existente;
- se registra exactamente una vez mediante `record_reentry(...)`;
- el resultado usa status `RECORDED`;
- Episode queda `AWAITING_REQUIREMENT`;
- stopping reason `NONE`;
- el budget restante se conserva;
- STOP antes de crear/admitir R(N+1).

Para budget 4, E3 → RR3 queda en `AWAITING_REQUIREMENT` con remaining 1.

## Re-entry terminal

Si no queda budget:
- el mismo owner registra el re-entry;
- Episode queda `CLOSED`;
- stopping reason `BUDGET_EXHAUSTED`;
- remaining 0;
- status `CLOSED`.

Esto preserva exactamente E2 → RR2 para budget 2 y permite E4 → RR4 para
budget 4.

## STOP

El bloque termina después del Reasoning re-entry y el registro en Episode.

No crea ni admite el siguiente requirement, no invoca Planning, Authorization,
Execution, Curiosity, Memory, World Model, Conversation, retry ni background work.
