# ROBY XI.2 — Long-horizon Investigation
## GREEN — Governed Resume Admission → Existing Evidence Acquisition Planning

**Baseline oficial de entrada:** 13.561 PASS + Ruff limpio.

## Cierre productivo

Se incorpora `app.governed_long_horizon_investigation_evidence_planning` como adaptador estrecho entre una `GovernedInvestigationResumeAdmission` ya admitida y la superficie canónica existente `GovernedEvidenceAcquisitionProductiveConsumptionV1`.

El owner de Planning permanece sin cambios en `planning_foundation`. El bridge no crea un planner, no reconstruye el requirement y no reutiliza el reentry histórico dependiente del step 2.

## Invariantes GREEN

- Sólo `ADMITTED` + `eligible_for_existing_planning=True` alcanza Planning.
- Planning recibe exactamente `admission.requirement`.
- Existe como máximo una invocación a la superficie productiva de Planning.
- El resultado preserva admission/thread/checkpoint/resume/episode/reasoning lineage, requirement/source/snapshot, plan id, planning status y el planning product existente.
- Una excepción de Planning o una incompatibilidad de lineage produce `REVIEW_REQUIRED` sin exponer producto válido.
- `eligible_for_authorization=True` sólo deriva de `PLANNED + PLANNABLE`.
- El bridge no autoriza, no ejecuta, no adquiere evidencia, no invoca capabilities, no rerunea Reasoning, no modifica Episode/Memory/World Model y no inicia background work.

## Corte de salida

El bloque termina exactamente en:

`Governed Resume Admission → Existing Evidence Acquisition Planning → authorization eligibility as derived data`

No forma parte de este GREEN:

`Existing Evidence Acquisition Plan → Existing Governed Authorization → Execution → Acquired Evidence → Reasoning Re-entry → Model Revision`.

## Residual siguiente

`Existing Evidence Acquisition Plan → Existing Governed Authorization`.
