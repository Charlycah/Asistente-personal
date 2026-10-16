# ROBY XI.2 — Long-horizon Investigation
## Contract RED — Governed Resume Candidate → Explicit Requirement Rebinding → Governed Resume Admission

**Baseline oficial de entrada:** 13.550 PASS + Ruff limpio.

## 1. Objetivo

Congelar el siguiente corte productivo sin implementar Planning:

`GovernedInvestigationResumeCandidate`
+ `GovernedPassiveInvestigationCheckpoint`
+ `DiscriminatingEvidenceRequirement` explícito
→ `GovernedInvestigationResumeAdmission`

El bridge debe restaurar la semántica exacta de la inquiry mediante **re-binding
explícito del requirement real**. No reconstruye requirements desde IDs.

## 2. Módulo contractual esperado

`app.governed_long_horizon_investigation_resume_admission`

Superficies mínimas:

- `GovernedInvestigationResumeAdmissionStatus`
- `GovernedInvestigationResumeAdmission`
- `GovernedLongHorizonInvestigationResumeAdmissionV1`
- `admit(...)`

## 3. Input obligatorio

`admit(...)` debe consumir exactamente:

- `GovernedPassiveInvestigationCheckpoint`
- `GovernedInvestigationResumeCandidate`
- `DiscriminatingEvidenceRequirement`

El requirement debe llegar como objeto semántico explícito.

Queda prohibido:
- reconstruirlo desde `requirement_id`;
- inferir hipótesis;
- inventar missing evidence;
- regenerar evidence codes;
- crear una nueva inquiry.

## 4. Lineage mínimo de salida

La admisión debe preservar:

- `admission_id`
- `thread_id`
- `checkpoint_id`
- `resume_id`
- `episode_id`
- `originating_reasoning_id`
- `requirement`
- `requirement_id`
- `source_reference`
- `world_snapshot_id`
- `status`
- `rationale_codes`
- `eligible_for_existing_planning`
- `source_fingerprint`

## 5. Status fail-closed

Contrato mínimo:

- `ADMITTED`
- `NOT_ELIGIBLE`
- `REVIEW_REQUIRED`
- `LINEAGE_MISMATCH`
- `REQUIREMENT_MISMATCH`
- `SNAPSHOT_MISMATCH`
- `BUDGET_EXHAUSTED`

Sólo un `GovernedInvestigationResumeCandidate` realmente elegible puede avanzar a
`ADMITTED`.

## 6. Gates obligatorios

El GREEN deberá comprobar:

1. resume candidate corresponde al checkpoint exacto;
2. thread ID exacto;
3. source lineage exacta;
4. requirement ID pertenece al checkpoint;
5. requirement object explícito coincide con ese ID;
6. requirement source coincide con checkpoint/resume;
7. requirement snapshot coincide con same-snapshot resume;
8. snapshot anterior y actual siguen siendo compatibles;
9. budget histórico no está agotado;
10. inquiry resuelta no se reactiva;
11. requirement previo no se reutiliza de forma silenciosa;
12. no se crea un episodio nuevo.

## 7. Límites de autoridad

La admisión debe ser explícitamente:

- `read_only = True`
- `planning_execution_authorized = False`
- `creates_plans = False`
- `invokes_capabilities = False`
- `executes_actions = False`
- `performs_reasoning = False`
- `persists_results = False`
- `modifies_memory = False`
- `modifies_world_model = False`
- `modifies_planning = False`
- `starts_background_process = False`
- `grants_authority = False`
- `creates_episode = False`

`eligible_for_existing_planning` significa únicamente que el objeto puede ser
presentado posteriormente a un gate de Planning ya existente o a una extensión
estrecha de ese owner.

No equivale a plan, autorización ni ejecución.

## 8. Prohibiciones estructurales

Este bloque no debe:

- llamar `GovernedLevel2BProductiveEntryFoundationV1`;
- fabricar `GovernedMultiStepInvestigationProductiveContinuation`;
- usar el planning re-entry especializado de step 2 como atajo;
- llamar Planning;
- llamar Authorization;
- llamar Execution;
- adquirir evidencia;
- rerun Reasoning;
- producir Model Vn+1;
- escribir Memory;
- escribir World Model.

## 9. Resultado RED

Ejecución observada:

**7 FAILED + 2 PASSED**

Los siete fallos son deliberados y prueban que todavía faltan:

1. módulo de resume admission;
2. objeto de admisión con lineage completo;
3. binding del requirement real;
4. gate explícito `admit(...)`;
5. status fail-closed;
6. límites no ejecutivos/no mutantes;
7. firma tipada exacta de input.

Los dos PASS prueban que:

- `DiscriminatingEvidenceRequirement` ya contiene la semántica necesaria para un
  re-binding real;
- checkpoint y resume candidate actuales siguen sin incorporar un bypass de Planning.

## 10. Regla GREEN

No debilitar este RED.

El próximo GREEN debe cerrar únicamente:

`Resume Candidate`
→ `Explicit Requirement Rebinding`
→ `Governed Resume Admission`

y detenerse antes de Evidence Acquisition Planning.

La baseline oficial permanece:

**13.550 PASS + Ruff limpio**
