# CAP-11 — Authorization step N → existing Execution re-entry — GREEN

Estado: GREEN quirúrgico pendiente de certificación local completa.

## Producción

Se generalizó exclusivamente
`GovernedMultiStepInvestigationExecutionReentryV1`.

No se creó executor, gateway, manager, loop ni autoridad nueva.

La admisión de Execution exige ahora alineación gobernada:
- `2 <= current_step <= max_acquisitions`;
- `consumed_acquisitions == current_step - 1`;
- el budget restante de Authorization coincide con el Episode;
- `remaining_acquisitions > 0` antes de ejecutar.

Después de una adquisición ACQUIRED válida:
- el Episode debe quedar en `AWAITING_REENTRY`;
- `consumed_acquisitions == current_step`;
- el budget restante puede ser mayor que cero;
- `eligible_for_reasoning_reentry=True`.

La elegibilidad es declarativa: este bloque no invoca Reasoning.

## Compatibilidad histórica

A2/E2 con budget 2 conserva el mismo owner, el mismo gateway y el mismo corte.
El bridge long-horizon E2 específico no fue generalizado.

## Corrección del harness RED

Durante GREEN se detectó que el fixture contractual N-step declaraba
`next discriminating observation`, mientras reutilizaba un reader histórico que
emitía `new discriminating observation`. Eso hacía que el gateway fallara por
mismatch de evidencia incluso después de retirar los guards E2.

Se corrigió sólo el harness contractual para que su reader emita exactamente la
evidencia declarada por el plan. No se relajó ninguna validación productiva.

## STOP

El bloque termina tras Execution + `record_acquisition(...)`.
No invoca Reasoning re-entry, no produce RR3/RR4, no crea requisitos, no replantea,
no reautoriza, no reintenta y no extiende budget.
