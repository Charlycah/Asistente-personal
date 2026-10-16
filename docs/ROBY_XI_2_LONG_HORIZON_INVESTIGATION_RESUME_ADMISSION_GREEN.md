# ROBY XI.2 — Long-horizon Investigation
## GREEN — Resume Candidate + Checkpoint + Exact Requirement → Governed Resume Admission

**Baseline oficial de entrada:** 13.550 PASS + Ruff limpio.

## 1. Cierre implementado

Se implementa únicamente:

`GovernedInvestigationResumeCandidate`
+ `GovernedPassiveInvestigationCheckpoint`
+ `DiscriminatingEvidenceRequirement` explícito
→ `GovernedInvestigationResumeAdmission`

El bloque termina antes de Evidence Acquisition Planning.

## 2. Nuevo owner-extension

Nuevo módulo:

`app/governed_long_horizon_investigation_resume_admission.py`

Contratos:
- `GovernedInvestigationResumeAdmissionStatus`
- `GovernedInvestigationResumeAdmission`
- `GovernedLongHorizonInvestigationResumeAdmissionV1`

Operación:
- `admit(...)`

## 3. Exact Requirement Rebinding

La admisión recibe el objeto real `DiscriminatingEvidenceRequirement`.

No reconstruye semántica desde IDs y no inventa:
- hypothesis IDs;
- missing evidence;
- evidence codes;
- source lineage;
- snapshot lineage.

Sólo el requirement actual exacto del checkpoint puede quedar admitido.

## 4. Gates

El admission valida:
- checkpoint exacto;
- thread exacto;
- resume status elegible;
- requirement actual exacto;
- source lineage;
- same-snapshot continuity;
- budget histórico disponible;
- límites de gobernanza del requirement.

Estados fail-closed:
- `ADMITTED`
- `NOT_ELIGIBLE`
- `REVIEW_REQUIRED`
- `LINEAGE_MISMATCH`
- `REQUIREMENT_MISMATCH`
- `SNAPSHOT_MISMATCH`
- `BUDGET_EXHAUSTED`

## 5. Gobernanza

`eligible_for_existing_planning=True` sólo aparece con `ADMITTED`.

La admisión:
- no crea plan;
- no autoriza Planning;
- no ejecuta capabilities;
- no ejecuta acciones;
- no realiza Reasoning;
- no persiste resultados;
- no modifica Memory;
- no modifica World Model;
- no modifica Planning;
- no inicia background;
- no crea un episodio;
- no concede autoridad.

## 6. Compatibilidad

El RED contractual anterior pasa sin ser debilitado.

Se añadieron 11 tests GREEN oficiales para:
- exact rebinding;
- pasividad/no mutación;
- checkpoint mismatch;
- thread mismatch;
- requirement mismatch;
- source mismatch;
- changed-snapshot review;
- snapshot tampering;
- resolved inquiry;
- exhausted budget;
- determinismo.

Perímetro de construcción ejecutado:
**106 PASS**

Incluye:
- RED de resume admission;
- GREEN de checkpoint/resume;
- RED previo de checkpoint/resume;
- lifecycle histórico de investigación multi-step;
- planning/authorization/execution/reasoning re-entry históricos;
- production import-cycle audit.

## 7. Alcance excluido

Este GREEN NO llama todavía:
- Evidence Acquisition Planning;
- Authorization;
- Execution;
- Evidence acquisition;
- Reasoning re-entry;
- Explanatory Model Revision.

Residual siguiente:

`Governed Resume Admission`
→ `Existing Evidence Acquisition Planning`

sin usar artificialmente el planning re-entry especializado de step 2.

## 8. Gate oficial esperado

Con 11 tests oficiales nuevos, la baseline esperada tras promoción local es:

**13.561 PASS + Ruff limpio**

Gate:
`ruff check .`
`pytest -q`
