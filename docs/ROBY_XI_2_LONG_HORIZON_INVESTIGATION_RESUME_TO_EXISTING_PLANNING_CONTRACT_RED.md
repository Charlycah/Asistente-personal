# ROBY XI.2 — Long-horizon Investigation
## Contract RED — Governed Resume Admission → Existing Evidence Acquisition Planning

**Baseline oficial de entrada:** 13.561 PASS + Ruff limpio.

## 1. Objetivo

Congelar el bridge mínimo desde una admisión gobernada ya certificada hacia Evidence Acquisition Planning existente, sin Authorization ni Execution.

## 2. Módulo contractual esperado

`app.governed_long_horizon_investigation_evidence_planning`

Superficies mínimas esperadas:

- `GovernedInvestigationEvidencePlanningStatus`
- `GovernedInvestigationEvidencePlanningResult`
- `GovernedLongHorizonInvestigationEvidencePlanningV1`
- `consume(admission)`

## 3. Owner

El módulo nuevo NO es autoridad de Planning.

Debe delegar exclusivamente en:

`GovernedEvidenceAcquisitionProductiveConsumptionV1`

con autoridad canónica:

`planning_foundation`

## 4. Contrato de admisión

Sólo una `GovernedInvestigationResumeAdmission` con status `ADMITTED` y `eligible_for_existing_planning=True` puede alcanzar Planning.

Una admisión no elegible debe retornar fail-closed con cero invocaciones de Planning.

## 5. Requirement exacto

Planning debe recibir exactamente `admission.requirement` por identidad de objeto.

Prohibido:

- reconstruir el requirement desde IDs;
- inventar missing evidence;
- reescribir hipótesis;
- cambiar source/snapshot;
- crear otra inquiry.

## 6. Invocación

El adapter permite como máximo una invocación al Planning existente por `consume(...)`.

Si la llamada falla, el resultado es `REVIEW_REQUIRED`.

## 7. Lineage de salida

El resultado debe preservar lineage de admisión y del planning product:

- admission/thread/checkpoint/resume/episode/reasoning;
- requirement/source/snapshot;
- plan ID;
- planning status;
- planning product existente.

## 8. Eligibility derivada

`eligible_for_authorization=True` únicamente cuando:

- bridge status = `PLANNED`;
- planning status = `PLANNABLE`.

El bridge NO autoriza.

## 9. Límites

Debe permanecer:

- `canonical_planning_authority = planning_foundation`;
- `planning_execution_authorized = False`;
- `execution_authorized = False`;
- `invokes_authorization = False`;
- `invokes_capabilities = False`;
- `acquires_evidence = False`;
- `invokes_reasoning = False`;
- `modifies_episode_state = False`;
- `modifies_memory = False`;
- `modifies_world_model = False`;
- `starts_background_process = False`.

## 10. Prohibición estructural

No reutilizar `GovernedMultiStepInvestigationPlanningReentryV1` como atajo, porque su contrato depende del step 2 de la continuación multi-step.

## 11. Residual posterior

El GREEN de este contrato debe detenerse antes de Authorization.

Residual posterior:

`Existing Evidence Acquisition Plan → Existing Governed Authorization`.
