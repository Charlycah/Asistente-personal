# CAP-11 — Planning step N → existing Authorization re-entry — CONTRACT RED

Estado: RED contractual deliberado.

## Autoridad congelada

No se crea una nueva autoridad de Authorization. El único owner de re-entry es
`GovernedMultiStepInvestigationAuthorizationReentryV1`, que reutiliza
`GovernedIndependenceAuthorizationBoundaryV1` y su productive consumption existente.

## Contrato N-step exigido

Un `GovernedInvestigationPlanningReentryResult` canónico puede entrar en Authorization
cuando conserva `PLANNED`, `PLANNABLE`, elegibilidad de Authorization, lineage exacto,
step gobernado dentro del budget, `consumed_acquisitions == current_step - 1` y budget
restante positivo.

El RED exige step 3/budget 4 y step 4/budget 4 sin retirar el soporte histórico exacto
P2/A2 con budget 2.

## STOP line

El corte termina en `GovernedInvestigationAuthorizationReentryResult`.
`MAY_INITIATE` sólo puede exponer `eligible_for_existing_execution=True`.
No se invoca Execution, no se produce E3/E4, no se invoca Reasoning, no se modifica
Episode, no se crea requirement, no se amplía budget y no se añade loop/manager/gateway.

## Fallos deliberados esperados

La producción reconciliada conserva todavía los guards históricos
`current_step != 2` y `remaining_acquisitions != 1`. Por ello deben fallar las pruebas
N-step de A3/A4 y la prueba que exige retirar esos guards. El caso histórico P2/A2 debe
seguir pasando.
