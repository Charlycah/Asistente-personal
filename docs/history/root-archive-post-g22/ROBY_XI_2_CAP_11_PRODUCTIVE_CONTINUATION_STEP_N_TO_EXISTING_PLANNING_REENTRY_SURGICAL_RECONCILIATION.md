# ROBY XI.2 — CAP-11 Productive Continuation step N → Existing Planning Re-entry
## Reconciliación arquitectónica quirúrgica

**Baseline de entrada:** 13.683 PASS + Ruff limpio (certificación local del usuario).  
**Naturaleza del corte:** reconciliación únicamente; no se generaliza producción en este documento.  
**Regla de gobierno:** una única autoridad por capacidad; no se crea planner, manager, gateway, loop ni episodio paralelo.

## 1. Objetivo exacto

Determinar el cambio mínimo y verificable para que una continuación gobernada de un episodio CAP-11 en cualquier `step N` válido bajo el presupuesto constitucional existente pueda reentrar **una sola vez** en la autoridad de Planning ya certificada, sin reabrir ni duplicar Planning y sin invocar Authorization, Execution, Reasoning, Curiosity, Memory, World Model, persistencia o background work.

El alcance termina en el producto canónico `GovernedInvestigationPlanningReentryResult`. Un resultado `PLANNABLE` puede conservar únicamente la elegibilidad declarativa para la Authorization ya existente; este bloque no invoca Authorization.

## 2. Estado constitucional ya certificado

La generalización anterior dejó `GovernedMultiStepInvestigationEpisodeBoundaryV1` como único owner del budget/step del episodio. El episodio admite un budget gobernado finito `1..4`, mantiene default histórico `2`, representa `current_step` N-step y sólo cierra por agotamiento cuando `consumed_acquisitions == max_acquisitions`.

Por tanto, el Episode owner ya puede producir de forma legítima un estado como:

- `status = READY_FOR_PLANNING`
- `current_step = 3`
- `consumed_acquisitions = 2`
- `max_acquisitions = 4`
- `remaining_acquisitions = 2`
- `requirement_ids = (R1, R2, R3)`

Ese estado no ejecuta Planning. Sólo declara que existe un nuevo requirement gobernado listo para reentrar en la Planning existente.

## 3. Owner productivo de continuación existente

El owner correcto sigue siendo:

`app/governed_multistep_investigation_productive_continuation.py`

- `GovernedMultiStepInvestigationProductiveContinuationV1`
- `GovernedMultiStepInvestigationProductiveContinuation`

No existe necesidad arquitectónica de crear `ProductiveContinuationV2`, `HorizonContinuationManager`, scheduler o loop.

### 3.1 Residual exacto encontrado

La superficie ya conserva correctamente:

- exact `episode_id`;
- exact `source_requirement` por objeto;
- transition/state identity;
- source/snapshot lineage;
- `current_step`;
- `remaining_acquisitions`;
- stopping reason;
- fingerprint con step y remaining budget;
- ausencia de Planning/Authorization/Execution/Reasoning side effects.

El único bloqueo productivo es la elegibilidad todavía especializada al ciclo histórico:

`current_step == 2 and remaining_acquisitions == 1`

La misma especialización aparece dos veces: en el `__post_init__` del producto y en `consume(...)`.

## 4. Owner de Planning re-entry existente

El owner correcto sigue siendo:

`app/governed_multistep_investigation_planning_reentry.py`

- `GovernedMultiStepInvestigationPlanningReentryV1`
- `GovernedInvestigationPlanningReentryResult`

Ese owner ya consume exactamente `GovernedMultiStepInvestigationProductiveContinuation`, llama una sola vez a `GovernedEvidenceAcquisitionProductiveConsumptionV1`, preserva el requirement exacto, rechaza reutilización de un `plan_id` previo y no modifica el Episode state.

No se necesita un nuevo planner ni una nueva ruta hacia `core.evidence_acquisition_planning`.

### 4.1 Residual exacto encontrado

`GovernedInvestigationPlanningReentryResult` ya es estructuralmente N-step: conserva `current_step` y `remaining_acquisitions` sin exigir step 2.

La única especialización real está en `_eligibility_error(...)`, que exige:

`current_step == 2 or remaining_acquisitions != 1` → `bounded_step_two_required`.

El resto del flujo de Planning es reutilizable sin crear otra autoridad.

## 5. Invariante N-step que debe reemplazar el supuesto step-2

La elegibilidad de Productive Continuation y Planning re-entry debe derivarse de la constitución del Episode, no de números históricos hard-coded.

Para un continuation productivo step N se debe exigir simultáneamente:

1. `decision is CONTINUE_ALLOWED`.
2. `resulting_state.status is READY_FOR_PLANNING`.
3. `source_requirement is not None` y se preserva por identidad.
4. `source_requirement.requirement_id == resulting_state.current_requirement_id`.
5. source y world snapshot son exactos en requirement, continuation y state.
6. `2 <= current_step <= max_acquisitions`.
7. `consumed_acquisitions == current_step - 1`.
8. `remaining_acquisitions > 0`.
9. `remaining_acquisitions == max_acquisitions - consumed_acquisitions` por el Episode owner.
10. continuation sigue siendo no ejecutiva: no Planning invocation en Productive Continuation y ninguna autorización de ejecución.

Este contrato hace válidos, por ejemplo:

- histórico budget 2: step 2, consumed 1, remaining 1;
- budget 4: step 2, consumed 1, remaining 3;
- budget 4: step 3, consumed 2, remaining 2;
- budget 4: step 4, consumed 3, remaining 1.

No hace válido step 1 como re-entry de continuación, ni un step que no tenga exactamente todas las adquisiciones anteriores consumidas.

## 6. Compatibilidad histórica obligatoria

El GREEN posterior deberá preservar byte-semánticamente el comportamiento certificado de budget 2:

- RR1 + R2 sigue produciendo una continuación step 2 elegible;
- el mismo R2 entra una sola vez a la Planning existente;
- P2 sigue siendo nuevo respecto a `state.plan_ids`;
- `PLANNABLE` continúa significando sólo `eligible_for_authorization=True`;
- no se autoriza ni ejecuta E2 desde Planning;
- los tests históricos step-2 deben seguir pasando sin reescritura para acomodar el nuevo comportamiento.

Los rationale/fingerprint históricos no deben cambiar innecesariamente para el caso budget 2.

## 7. Superficie mínima de cambio para RED/GREEN

Sólo deben generalizarse productivamente:

1. `app/governed_multistep_investigation_productive_continuation.py`
2. `app/governed_multistep_investigation_planning_reentry.py`

El RED debe añadir un contrato nuevo N-step y usar los tests históricos como guards de compatibilidad.

No es necesario modificar en este corte:

- `app/governed_multistep_investigation_episode.py` — ya generalizado y certificado;
- `app/governed_long_horizon_investigation_continuity.py` — ya generalizado y certificado;
- `core/evidence_acquisition_planning.py` — owner de Planning ya suficiente;
- `app/governed_evidence_acquisition_productive_consumption.py` — superficie canónica ya suficiente.

## 8. El bridge P2 histórico NO debe generalizarse aquí

`app/governed_long_horizon_investigation_p2_planning_reentry.py` está deliberadamente especializado a R2/P2, step 2 y al ciclo long-horizon histórico de dos adquisiciones.

No debe convertirse en un bridge N-step mediante condicionales `if step == 3/4`, renombrados ambiguos o expansión de sus contratos P2. Hacerlo mezclaría compatibilidad histórica con la nueva capacidad generalizada y volvería más difícil certificar autoridad y lineage.

El camino N-step de este corte es el owner canónico:

`GovernedMultiStepInvestigationProductiveContinuationV1`
→ `GovernedMultiStepInvestigationPlanningReentryV1`
→ existing Evidence Acquisition Planning.

Si más adelante la capa long-horizon/resume necesita un admission/wiring genérico para step N, deberá reconciliarse como un bloque de wiring separado que consuma estos owners ya generalizados; nunca como un segundo planner.

## 9. STOP line del próximo GREEN

El próximo GREEN debe detenerse inmediatamente después de producir el exacto `GovernedInvestigationPlanningReentryResult`.

Puede exponer:

- `status = PLANNED`;
- exact `planning_product`;
- exact requirement lineage;
- nuevo `plan_id`;
- exact source/snapshot;
- exact `current_step` y budget;
- `eligible_for_authorization=True` sólo si el Planning canónico devuelve `PLANNABLE`.

No puede:

- invocar Authorization;
- producir A3/A4;
- invocar Execution;
- producir E3/E4;
- invocar Reasoning re-entry;
- crear otro requirement;
- incrementar step o budget;
- modificar Episode state;
- ejecutar capabilities;
- persistir;
- tocar Memory/World Model;
- iniciar background work.

## 10. Fail-closed N-step

Debe resultar `NOT_ELIGIBLE` sin invocar Planning cuando falle cualquier precondición estructural N-step: state no `READY_FOR_PLANNING`, requirement ausente o distinto, lineage roto, step fuera de budget, `consumed_acquisitions != current_step - 1`, budget agotado o continuation no elegible.

Si la llamada única al owner Planning falla, el resultado sigue siendo `REVIEW_REQUIRED`, sin retry. Si el Planning devuelve lineage incorrecto o reutiliza un plan previo, también se conserva el fail-closed histórico.

## 11. RED recomendado

Un contrato RED quirúrgico debería congelar como mínimo:

- Productive Continuation step 3 / budget 4 pasa a `eligible_for_existing_planning=True`.
- step 4 / budget 4 también es elegible cuando consumed=3.
- state incoherente (`current_step != consumed+1`) nunca es elegible.
- step 1 nunca se trata como re-entry de continuación.
- Planning re-entry consume exactamente una vez el continuation step 3 y conserva el exacto R3.
- nuevo P3 no reutiliza P1/P2.
- PLANNABLE P3 sólo expone Authorization eligibility; no Authorization invocation.
- caso histórico step 2 / budget 2 conserva identidad, semántica y tests existentes.
- no nuevos planners/managers/gateways/loops.

El RED no debe tocar todavía Authorization, Execution ni Reasoning N-step.

## 12. Dictamen

**No falta una nueva capacidad de Planning. Falta retirar dos guards históricos step-2 que quedaron dentro de los owners ya correctos.**

La generalización correcta es local y gobernada: Productive Continuation debe derivar elegibilidad de la estructura N-step certificada del Episode y `GovernedMultiStepInvestigationPlanningReentryV1` debe aceptar esa misma estructura, manteniendo una sola invocación al Planning existente.

Después de certificar este bloque, el siguiente residual real será:

`exact planned step N → existing Authorization re-entry`,

que deberá reconciliarse por separado y sin convertir esta etapa en orquestación automática.
