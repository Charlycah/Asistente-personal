# ROBY XI.2 — CAP-11 Productive Continuation step N → Existing Planning re-entry — GREEN

## Estado

GREEN quirúrgico sobre baseline productiva certificada **13.683 PASS + Ruff limpio**.

## Autoridades preservadas

- `GovernedMultiStepInvestigationEpisodeBoundaryV1` continúa siendo la única autoridad de estado/budget/stopping del episodio.
- `GovernedMultiStepInvestigationProductiveContinuationV1` continúa siendo el único owner de admisión productiva de la siguiente requirement.
- `GovernedMultiStepInvestigationPlanningReentryV1` continúa siendo el único owner de reentrada de investigación hacia la Planning existente.
- La Planning real continúa delegada a `GovernedEvidenceAcquisitionProductiveConsumptionV1` / `planning_foundation`.
- No se crea P3/P4 planner, manager, gateway, research loop ni autoridad paralela.

## Cambio productivo mínimo

La elegibilidad deja de estar codificada como `current_step == 2` y `remaining_acquisitions == 1`. Se deriva ahora exclusivamente de las invariantes ya certificadas del Episode N-step:

- decisión `CONTINUE_ALLOWED`;
- episodio `READY_FOR_PLANNING`;
- `2 <= current_step <= max_acquisitions`;
- `consumed_acquisitions == current_step - 1`;
- `remaining_acquisitions > 0`;
- requirement exacta y actual del episodio;
- source/snapshot exactos.

El caso histórico **step 2 / budget 2** permanece dentro de esas mismas invariantes y conserva el mismo camino productivo.

## Planning re-entry

`GovernedMultiStepInvestigationPlanningReentryV1.consume(...)` sigue realizando como máximo una llamada a la Planning existente. Un resultado `PLANNABLE` sólo expone `eligible_for_authorization=True`; este bloque no invoca Authorization, Execution ni Reasoning y no modifica el Episode state. La protección contra reutilización de `plan_id` previo permanece activa.

## Compatibilidad histórica

Se actualiza únicamente una aserción contractual histórica que exigía el texto ya obsoleto `bounded_step_two_required`. El contrato conserva su propósito original —firma compatible, `READY_FOR_PLANNING`, no reutilización de plan y ausencia de autoridad downstream— pero reconoce el guard N-step `governed_step_budget_alignment_required`.

## Frontera de cierre

Este GREEN termina en Planning. No se generalizan el bridge long-horizon P2, Authorization re-entry, Execution re-entry ni Reasoning closure. A3/A4/E3/E4/RR3/RR4 continúan fuera de alcance hasta reconciliación separada.
