# CAP-11 — Planning step N → existing Authorization re-entry — GREEN

Estado: GREEN quirúrgico pendiente de certificación local completa.

## Cambio productivo mínimo

Se retiraron únicamente los guards históricos `current_step != 2` y
`remaining_acquisitions != 1` de
`GovernedMultiStepInvestigationAuthorizationReentryV1`.

La elegibilidad ahora deriva de la estructura N-step ya certificada del Episode:

- `2 <= current_step <= max_acquisitions`;
- `consumed_acquisitions == current_step - 1`;
- `remaining_acquisitions > 0`.

El resto del owner, su delegación a la autoridad existente de Authorization, lineage,
fail-closed y compatibilidad P2/A2 permanecen sin nueva autoridad.

## STOP

El resultado termina en `GovernedInvestigationAuthorizationReentryResult`.
`MAY_INITIATE` sólo expone elegibilidad declarativa para existing Execution.
No se invoca Execution, no se produce E3/E4, no se invoca Reasoning, no se modifica
Episode y no se crea loop/manager/gateway.
