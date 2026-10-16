# ROBY XI.2 — CAP-11 Productive Continuation step N → Existing Planning Re-entry
## Contrato RED

**Baseline contractual:** 13.683 PASS + Ruff limpio.  
**Predecesor:** `ROBY_XI_2_CAP_11_PRODUCTIVE_CONTINUATION_STEP_N_TO_EXISTING_PLANNING_REENTRY_SURGICAL_RECONCILIATION.md`.  
**Naturaleza:** RED deliberado; producción permanece sin generalizar en este bloque.

## Propósito

Congelar el contrato mínimo para retirar únicamente los guards históricos `step 2 / remaining 1` de los owners canónicos ya existentes, sin crear un planner nuevo y sin abrir Authorization, Execution o Reasoning N-step.

## Owners congelados

La única superficie productiva permitida para el GREEN posterior es:

- `app/governed_multistep_investigation_productive_continuation.py`
- `app/governed_multistep_investigation_planning_reentry.py`

Planning sigue perteneciendo a la autoridad existente consumida por `GovernedMultiStepInvestigationPlanningReentryV1`. No se crea `P3` owner, `PlanningV2`, manager de horizonte, loop ni scheduler.

## Contrato N-step

Una continuación productiva es elegible para Planning cuando conserva una transición `CONTINUE_ALLOWED` a `READY_FOR_PLANNING`, el requirement actual exacto y su source/snapshot, y la constitución del episodio demuestra que todas las adquisiciones previas al step actual fueron consumidas y todavía queda presupuesto. El contrato admite step 2, 3 o 4 bajo el hard-cap constitucional 4; no convierte el budget en autorización de ejecución.

El Planning re-entry existente debe aceptar ese mismo continuation N-step, invocar exactamente una vez la superficie canónica existente de Evidence Acquisition Planning, preservar requirement/source/snapshot/episode/step/budget, producir un `plan_id` nuevo respecto del lineage previo y detenerse en `GovernedInvestigationPlanningReentryResult`.

## Compatibilidad histórica obligatoria

El caso histórico `step 2 / max_acquisitions 2 / remaining 1` permanece exactamente soportado. Los tests históricos no se reescriben para acomodar el nuevo contrato y el bridge long-horizon P2 permanece especializado y sin cambios.

## STOP antes de Authorization

Un planning `PLANNABLE` sólo puede declarar `eligible_for_authorization=True`. Este bloque no invoca Authorization, no produce A3/A4, no ejecuta capabilities, no produce E3/E4, no reentra Reasoning, no altera el Episode state, no incrementa step/budget y no inicia retry/background/persistencia/Memory/World Model.

## RED deliberado

`tests/architecture/test_cap11_productive_continuation_step_n_to_existing_planning_reentry_contract_red.py` congela:

1. step 3 / budget 4 debe ser elegible para existing Planning;
2. step 4 / budget 4 debe ser elegible;
3. step 3 debe entrar exactamente una vez en `GovernedMultiStepInvestigationPlanningReentryV1` y preservar R3;
4. el plan de step 3 debe ser nuevo y sólo authorization-eligible;
5. step 2 / budget 2 permanece productivamente idéntico;
6. los guards textuales step-2 deben desaparecer sin añadir autoridades downstream.

En la baseline 13.683 los fallos esperados son exclusivamente los que demuestran que Productive Continuation y Planning re-entry todavía mantienen los guards históricos step-2.
