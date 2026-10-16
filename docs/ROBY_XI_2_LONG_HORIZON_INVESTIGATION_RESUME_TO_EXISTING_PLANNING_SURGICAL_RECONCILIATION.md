# ROBY XI.2 — Long-horizon Investigation
## Reconciliación quirúrgica — Governed Resume Admission → Existing Evidence Acquisition Planning

**Baseline oficial de entrada:** 13.561 PASS + Ruff limpio.

## 1. Corte de entrada certificado

El bloque anterior queda cerrado en:

`GovernedPassiveInvestigationCheckpoint`
+ `GovernedInvestigationResumeCandidate`
+ `DiscriminatingEvidenceRequirement` explícito
→ `GovernedInvestigationResumeAdmission`

No se reabre salvo incompatibilidad real. La inspección de la baseline no encontró una incompatibilidad que obligue a modificar ese GREEN.

## 2. Owner canónico ya existente

Evidence Acquisition Planning ya existe y su autoridad canónica es:

`planning_foundation`

Superficies productivas existentes:

- `core.evidence_acquisition_planning.GovernedEvidenceAcquisitionPlanner`
- `app.governed_evidence_acquisition_productive_consumption.GovernedEvidenceAcquisitionProductiveConsumptionV1`

Por tanto el residual NO necesita ni permite un planner nuevo.

## 3. Superficie histórica que NO corresponde reutilizar directamente

Existe:

`app.governed_multistep_investigation_planning_reentry.GovernedMultiStepInvestigationPlanningReentryV1`

pero su contrato está especializado en la continuación multi-step inmediata y exige, entre otras invariantes:

- `current_step == 2`;
- `remaining_acquisitions == 1`;
- `GovernedMultiStepInvestigationProductiveContinuation`;
- estado `READY_FOR_PLANNING` derivado de ese flujo.

Usarlo para long-horizon resume introduciría dependencia artificial del step 2 y mezclaría dos contratos temporales distintos.

## 4. Corte productivo exacto

El siguiente GREEN debe cerrar únicamente:

`GovernedInvestigationResumeAdmission (ADMITTED)`
→ adapter estrecho de admisión
→ `GovernedEvidenceAcquisitionProductiveConsumptionV1.consume(requirement)`
→ plan existente bajo `planning_foundation`

La salida del adapter puede exponer el producto existente y lineage de la admisión, pero no puede convertirse en una segunda autoridad de Planning.

## 5. Input mínimo

El adapter debe consumir:

- una `GovernedInvestigationResumeAdmission` ya producida por el bloque certificado;
- el registry necesario para construir/reutilizar la superficie productiva existente de Evidence Acquisition Planning.

El requirement usado por Planning debe ser exactamente `admission.requirement`; no se reconstruye desde `requirement_id`.

## 6. Gates previos a invocar Planning

Planning sólo puede invocarse cuando:

1. `admission.status == ADMITTED`;
2. `admission.eligible_for_existing_planning is True`;
3. `admission.requirement_id == admission.requirement.requirement_id`;
4. source y snapshot de la admisión coinciden con el requirement explícito;
5. la admisión preserva `canonical_planning_authority == planning_foundation`;
6. la admisión continúa siendo no ejecutiva/no mutante.

Cualquier otra admisión falla cerrada y no llama Planning.

## 7. Postcondiciones tras una única invocación

Si Planning responde correctamente, el adapter debe preservar exactamente:

- `admission_id`;
- `thread_id`;
- `checkpoint_id`;
- `resume_id`;
- `episode_id`;
- `originating_reasoning_id`;
- `requirement_id`;
- `source_reference`;
- `world_snapshot_id`;
- `plan_id` del producto existente;
- `EvidenceAcquisitionPlanningStatus`;
- producto de `GovernedEvidenceAcquisitionProductiveConsumptionV1` sin reescribirlo.

Sólo `PLANNABLE` puede producir `eligible_for_authorization = True`. `PARTIALLY_PLANNABLE`, `AMBIGUOUS` y `NO_CAPABILITY_AVAILABLE` quedan visibles pero no son authorization-eligible.

## 8. Fail-closed

El adapter debe quedar en `NOT_ELIGIBLE` sin invocar Planning para una admisión no admitida.

Si la única llamada al Planning existente falla, o devuelve lineage incompatible con la admisión, el resultado debe quedar en `REVIEW_REQUIRED`, sin plan productivo expuesto como válido y sin Authorization.

## 9. Límites de autoridad

Este bloque:

- no crea planner alternativo;
- no modifica `planning_foundation`;
- no selecciona capability para ejecución;
- no autoriza;
- no ejecuta;
- no adquiere evidencia;
- no rerunea Reasoning;
- no revisa Explanatory Model;
- no escribe Memory;
- no escribe World Model;
- no modifica episode state;
- no crea episodio;
- no inicia background work.

## 10. Corte de salida exacto

El GREEN debe detenerse en:

`Governed Resume Admission`
→ `Existing Evidence Acquisition Planning`
→ `eligible_for_authorization` solamente como dato derivado del status `PLANNABLE`.

Quedan fuera del bloque:

`Authorization → Execution → Acquired Evidence → Reasoning Re-entry → Model Revision`.

## 11. Decisión arquitectónica

No hay incompatibilidad real que justifique reabrir Resume Admission.

La implementación correcta es una **superficie adaptadora estrecha** en `app/`, cuyo único acto productivo permitido es presentar el requirement explícito ya admitido a la autoridad de Planning existente exactamente una vez.

Esto preserva una autoridad por capacidad y mantiene el cerebro unificado.
