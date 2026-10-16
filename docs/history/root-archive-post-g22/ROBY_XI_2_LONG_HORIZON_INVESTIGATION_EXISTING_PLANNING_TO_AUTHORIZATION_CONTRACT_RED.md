# ROBY XI.2 — Long-horizon Investigation
## Contract RED — Existing Evidence Acquisition Plan → Existing Governed Authorization

**Baseline oficial de entrada:** 13.568 PASS + Ruff limpio.

## 1. Objetivo

Congelar el bridge mínimo desde el planning product existente y elegible hacia la autoridad de autorización ya existente, sin Execution ni adquisición de evidencia.

## 2. Módulo contractual esperado

`app.governed_long_horizon_investigation_evidence_authorization`

Superficies mínimas esperadas:

- `GovernedInvestigationEvidenceAuthorizationStatus`
- `GovernedInvestigationEvidenceAuthorizationResult`
- `GovernedLongHorizonInvestigationEvidenceAuthorizationV1`
- `consume(planning_result)`

## 3. Owner canónico

El módulo nuevo NO es autoridad de Authorization.

Debe delegar exclusivamente en:

`GovernedIndependenceAuthorizationBoundaryV1`

con autoridad canónica:

`governed_independence_authorization_boundary`

La decisión existente debe exponerse mediante `GovernedIndependenceAuthorizationProductiveConsumptionV1` sin recalcularla.

## 4. Elegibilidad de entrada

Sólo un `GovernedInvestigationEvidencePlanningResult` con:

- status `PLANNED`;
- planning status `PLANNABLE`;
- `eligible_for_authorization=True`;
- planning product presente;
- lineage consistente;
- estado no ejecutivo;

puede alcanzar Authorization.

Cualquier otra entrada debe fallar cerrado con cero invocaciones de Authorization.

## 5. Producto exacto

Authorization debe recibir exactamente `planning_result.planning_product`.

Prohibido:

- reconstruir el planning product;
- volver a ejecutar Planning;
- crear un plan nuevo;
- seleccionar otra capability;
- alterar requirement/plan/source/snapshot.

## 6. Invocación

El adapter permite como máximo una invocación a `GovernedIndependenceAuthorizationBoundaryV1.evaluate(...)` por `consume(...)`.

Una excepción produce `REVIEW_REQUIRED`.

## 7. Lineage de salida

El resultado debe preservar como mínimo:

- admission/thread/checkpoint/resume/episode/reasoning;
- requirement/source/snapshot;
- plan ID y planning product;
- authorization report/product;
- authorization ID y decision.

## 8. Eligibility derivada

`eligible_for_existing_execution=True` únicamente cuando:

- bridge status = `AUTHORIZED`;
- decision = `MAY_INITIATE`.

La existencia de una autorización consumida no implica ejecución automática.

## 9. Límites

Debe permanecer:

- `canonical_authorization_authority = governed_independence_authorization_boundary`;
- `execution_authorized = False`;
- `invokes_execution_gateway = False`;
- `invokes_capabilities = False`;
- `acquires_evidence = False`;
- `invokes_reasoning = False`;
- `modifies_episode_state = False`;
- `modifies_memory = False`;
- `modifies_world_model = False`;
- `starts_background_process = False`.

## 10. Prohibición estructural

No reutilizar `GovernedMultiStepInvestigationAuthorizationReentryV1` como atajo. Su contrato pertenece al reentry multi-step histórico y contiene precondiciones de step/budget que no forman parte de esta ruta.

## 11. Residual posterior

El GREEN debe detenerse antes de Execution.

Residual posterior:

`Existing Governed Authorization → Existing Governed Execution Gateway`.
