# CAP-11 — RR(N) canonical handoff → requirement admission — Reconciliación quirúrgica suplementaria

Estado: reconciliación cerrada. Sin cambios de producción.

## Hallazgo

El cierre N-step certificado de Reasoning entrega `GovernedInvestigationReasoningClosureResult`.
La integración histórica RR1→R2, `GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1`, consume exclusivamente `GovernedInvestigationReasoningReentryRecordingResult`.

Ambos resultados representan el mismo hecho gobernado necesario para esta frontera: un re-entry canónico ya ejecutado una vez, ya registrado una vez en el Episode, con lineage preservado y Episode detenido en `AWAITING_REQUIREMENT` cuando queda budget.

## Decisión de autoridad

No se crea adapter, DTO, manager, bridge, planner ni owner paralelo.

El owner de integración existente `GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1` se conserva y debe admitir dos formas canónicas de entrada:

- `GovernedInvestigationReasoningReentryRecordingResult` para la ruta histórica RR1→R2;
- `GovernedInvestigationReasoningClosureResult` para RR(N) en la ruta N-step certificada.

La implementación puede normalizar internamente los hechos de lineage comunes, pero esa normalización no constituye una nueva autoridad ni una nueva capacidad pública.

## Hechos mínimos comunes

Para la ruta N-step, el admission debe derivar directamente del closure existente:

- `status == RECORDED`;
- `reasoning_reentry` existe y conserva `reentry_id` y `evidence_id`;
- `reasoning_reentry_invocation_count == 1`;
- `episode_record_invocation_count == 1`;
- `resulting_episode_state.status == AWAITING_REQUIREMENT`;
- `resulting_episode_state` conserva `episode_id`, `originating_reasoning_id`, `source_reference` y `world_snapshot_id`;
- `2 <= current_step <= max_acquisitions - 1` antes de admitir R(N+1);
- `consumed_acquisitions == current_step`;
- `remaining_acquisitions > 0`;
- el evidence de RR(N) está presente en el revised report;
- no se reutiliza ni se inventa lineage histórico (`thread_id` / `checkpoint_id`) que el closure N-step no posee.

## Contrato de salida

La autoridad de discriminación sigue siendo `GovernedMultiHypothesisProductiveConsumptionV1` y se invoca exactamente una vez cuando la entrada es elegible.

- 0 requirements: `CLOSED_NO_REQUIREMENT`, Episode `CLOSED`, `NO_NEW_REQUIREMENT`, STOP.
- 1 requirement: admitir exactamente R(N+1) mediante `GovernedMultiStepInvestigationProductiveContinuationV1`, Episode `READY_FOR_PLANNING`, `current_step += 1`, consumed sin cambio, remaining sin cambio, STOP antes de Planning.
- >1 requirements: `REVIEW_REQUIRED`, sin continuation.

La salida existente puede conservar `thread_id` y `checkpoint_id` para compatibilidad histórica; para la ruta N-step esos campos no deben falsificarse. Deben representarse de forma explícitamente ausente/neutral si el contrato de resultado se generaliza.

## Preservación histórica

RR1→R2 con `GovernedInvestigationReasoningReentryRecordingResult` debe seguir pasando sin cambio observable de comportamiento, identidad de requirement, cardinalidad, invocation counts ni STOP antes de Planning.

## Frontera

STOP absoluto después de R(N+1). No Planning, Authorization, Execution ni nuevo Reasoning en este bloque.

## Siguiente movimiento

RED contractual mínimo: RR2→R3 + RR3→R4 + zero-requirement stop + preservación exacta RR1→R2 + rechazo de closure terminal + STOP antes de Planning.
