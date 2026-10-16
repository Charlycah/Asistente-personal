# CAP-11 — Execution step N → existing Reasoning re-entry — CONTRACT RED

Estado: RED contractual.

## Contrato congelado

La misma autoridad existente debe aceptar un
`GovernedInvestigationExecutionReentryResult` ACQUIRED de step N y:

1. invocar exactamente una vez el existing Reasoning re-entry;
2. preservar execution / authorization / requirement / plan / source / snapshot;
3. registrar exactamente una vez el re-entry mediante el Episode owner existente;
4. producir un resultado intermedio no terminal cuando quede budget;
5. producir cierre terminal cuando el budget quede agotado;
6. detenerse antes de crear o admitir R(N+1).

## RR3 intermedio

Para budget 4, E3 ACQUIRED debe producir RR3 registrado:
- un Reasoning re-entry;
- un `record_reentry(...)`;
- Episode `AWAITING_REQUIREMENT`;
- remaining 1;
- stopping reason `NONE`;
- no cierre;
- no R4;
- no Planning / Authorization / Execution.

## RR4 terminal

Para budget 4, E4 ACQUIRED debe producir RR4:
- un Reasoning re-entry;
- un `record_reentry(...)`;
- Episode `CLOSED`;
- remaining 0;
- stopping reason `BUDGET_EXHAUSTED`.

## Compatibilidad histórica

E2 → RR2 con budget 2 debe continuar exactamente soportado como cierre terminal.

## Prohibiciones

No segundo Reasoning owner, no planner, no authorization owner, no executor,
no loop, no scheduler, no retry, no Memory, no World Model, no conversation,
no background work y no creación/admisión del siguiente requirement.
