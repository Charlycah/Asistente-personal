# CAP-11 — RR(N) → R(N+1) — GREEN quirúrgico

Estado: GREEN local dirigido.

Se generalizó exclusivamente `GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1` para admitir:

- el `GovernedInvestigationReasoningReentryRecordingResult` histórico de RR1→R2;
- el `GovernedInvestigationReasoningClosureResult` canónico de la ruta N-step.

No se creó adapter, owner, manager, planner ni bridge paralelo.

El admission N-step exige closure `RECORDED`, una invocación de Reasoning, un registro Episode, lineage exacto, `AWAITING_REQUIREMENT`, budget restante y alignment `consumed_acquisitions == current_step`.

La admisión válida deriva dinámicamente `current_step + 1`, conserva consumed y remaining, deja Episode `READY_FOR_PLANNING` y se detiene sin invocar Planning.

El closure terminal queda `NOT_ELIGIBLE` y no discrimina.

Compatibilidad histórica: RR1→R2 conserva su entrada, metadata histórica y rationale de admisión R2. La ruta N-step no inventa `thread_id` ni `checkpoint_id`; esos campos se representan como ausentes.

Certificación dirigida observada:

- RED nuevo + RR1→R2 histórico: `9 passed`.
- superficie ampliada Reasoning N-step + RED/GREEN nuevo + RR1→R2 + Productive Continuation: `23 passed`.
- `compileall`: limpio.

`ruff` no está disponible en este entorno, por lo que Ruff global debe certificarse localmente antes de declarar nueva baseline oficial.
