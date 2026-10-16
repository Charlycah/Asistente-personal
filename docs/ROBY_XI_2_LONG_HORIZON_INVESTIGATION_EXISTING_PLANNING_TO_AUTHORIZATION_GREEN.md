# ROBY XI.2 — Long-horizon Investigation
## GREEN — Existing Evidence Acquisition Plan → Existing Governed Authorization

**Baseline oficial de entrada:** 13.568 PASS + Ruff limpio.

## Estado

GREEN implementado sobre el contrato RED congelado. El nuevo módulo
`app.governed_long_horizon_investigation_evidence_authorization` es un adapter estrecho y
no una autoridad nueva.

## Corte productivo

`GovernedInvestigationEvidencePlanningResult`
→ `GovernedIndependenceAuthorizationBoundaryV1.evaluate(planning_product)`
→ `GovernedIndependenceAuthorizationProductiveConsumptionV1.consume(report)`
→ resultado long-horizon de autorización gobernada.

Sólo `PLANNED + PLANNABLE + eligible_for_authorization=True`, con producto presente,
lineage exacto y estado no ejecutivo, alcanza la autoridad. Cualquier otra entrada falla
cerrado sin invocar Authorization.

La autoridad recibe exactamente `planning_result.planning_product`; no hay replanning,
selección alternativa de capability ni reconstrucción del plan.

## Semántica

Una evaluación canónica exitosa produce status bridge `AUTHORIZED` y conserva sin
reinterpretar la decisión existente (`MAY_INITIATE`, `MUST_ASK`, `MUST_ABSTAIN` o
`REVIEW_REQUIRED`). `eligible_for_existing_execution=True` deriva únicamente de
`AUTHORIZED + MAY_INITIATE`.

Una excepción o un mismatch de lineage produce `REVIEW_REQUIRED` sin exponer producto
de autorización.

## Límites preservados

El bridge mantiene `execution_authorized=False`, no invoca execution gateway, no ejecuta
capabilities, no adquiere evidencia, no modifica Memory/world-model/episode y no inicia
procesos de background. La autoridad canónica permanece
`governed_independence_authorization_boundary`.

No se reutiliza `GovernedMultiStepInvestigationAuthorizationReentryV1`.

## Residual posterior

`Existing Governed Authorization → Existing Governed Execution Gateway`.
