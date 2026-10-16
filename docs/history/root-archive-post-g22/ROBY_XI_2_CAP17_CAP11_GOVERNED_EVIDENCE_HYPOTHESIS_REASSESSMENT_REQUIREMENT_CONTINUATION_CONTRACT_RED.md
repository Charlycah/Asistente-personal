# CAP-17/CAP-11 — Governed Evidence → Existing Hypothesis Reassessment → Requirement Continuation — CONTRACT RED

Estado: RED contractual abierto después de GATE 1.C.

## Propósito

Cerrar únicamente el residual entre una evidencia gobernada ya reingresada y registrada en el Episode CAP-11 y la authority existente que admite R(N+1).

La capacidad NO crea una segunda ruta de Reasoning, Requirement generation, Planning ni adquisición. El owner cognitivo del hypothesis product permanece `governed_reasoning`; el owner de continuation permanece CAP-11.

## Frontera congelada

1. Todo `DiscriminatingEvidenceRequirement` producido por la discriminación canónica debe conservar lineage explícito hacia el `GovernedHypothesisDeepeningReport.report_id` exacto que lo originó. La coincidencia por `hypothesis_ids + source_reference + world_snapshot_id` no sustituye esa identidad.
2. El resultado productivo CAP-17 debe conservar el `GovernedLocalEvidenceReasoningReentryResult` ya producido; no puede perder `reentry_id`, `evidence_id` ni `reasoning_result` antes de la continuación.
3. La reevaluación del mismo conjunto de hipótesis pertenece a la authority existente `governed_reasoning`. Debe existir un puerto explícito sobre la foundation canónica de hypothesis deepening/reassessment; no un manager/runtime/agent CAP-17 paralelo.
4. Ese puerto debe ser source-agnostic respecto del transporte de adquisición: no debe depender semánticamente de `GovernedLocalEvidenceReasoningReentryResult` ni de `GovernedLevel2ReasoningReentryResult` como authorities alternativas. La evidencia ya admitida debe llegar por identidad/artefacto gobernado y el resultado de Reasoning existente.
5. La reevaluación debe preservar el mismo conjunto de hypothesis IDs y propositions, `source_reference` y `world_snapshot_id`; debe producir un `GovernedHypothesisDeepeningReport` nuevo y auditable, sin establecer verdad ni causalidad.
6. La evidencia nueva debe ser realmente aplicada en el revised hypothesis product. Anexar un `evidence_id` sin evaluación epistemológica no satisface el contrato.
7. Después del revised hypothesis product se reutilizan, sin reemplazo, `GovernedMultiHypothesisProductiveConsumptionV1`, `GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1`, `GovernedMultiStepInvestigationProductiveContinuationV1` y `evaluate_continuation`.
8. El camino productivo CAP-17 debe respetar orden causal: local Reasoning re-entry → Episode recording → hypothesis reassessment → existing R(N+1) admission.
9. El bloque termina antes de Planning N+1. No Planning, Authorization, Execution, segunda adquisición, segunda llamada a Reasoning, Memory, Learning, World Model mutation, question generation ni background process.
10. `.roby/config.json` y `credencial.json` permanecen intactos.

## API mínima esperada por el RED

El RED no congela nombres de una nueva clase de authority. Congela que `GovernedHypothesisDeepener`, como foundation canónica ya existente bajo `governed_reasoning`, exponga una operación explícita `reassess_with_governed_evidence(...)` o equivalente exactamente compatible con ese ownership. Para evitar una implementación paralela, el test contractual exige este puerto sobre la authority existente.

La provenance exacta se congela con `source_report_id` en `DiscriminatingEvidenceRequirement`, porque el requirement es el producto que cruza desde discriminación hacia el Episode y ya viaja por todo CAP-11. El discriminador existente debe poblar ese campo con el `report.report_id` que realmente originó R(N).

## Expected RED

El baseline productivo previo debe permanecer conceptualmente intacto. El nuevo archivo contractual debe fallar sólo por el seam ausente:

- falta `source_report_id` en `DiscriminatingEvidenceRequirement`;
- el discriminador todavía no propaga ese lineage al requirement;
- `GovernedProductiveReasoningLibraryInvocationResult` todavía pierde el local re-entry;
- `GovernedHypothesisDeepener` todavía no expone el reassessment productivo;
- el contributor CAP-17 todavía se detiene después de `record_local_evidence_reentry` y no alcanza la admission CAP-11 existente.

No se modifica producción en este RED.

## RED observado en la copia de trabajo

Ejecución focal del nuevo contrato:

`7 failed, 2 passed`

Los siete fallos corresponden exclusivamente a la frontera nueva congelada arriba. Dos guardrails del mismo archivo permanecen verdes: ausencia de una authority cognitiva paralela y conservación de la admission CAP-11 existente como owner de continuation.

Slice de regresión adyacente, sin tocar producción:

`31 passed`

Incluye Episode recording CAP-17/CAP-11, RR(N) → R(N+1), explanatory-model revision y N-step full cycle.

No se ejecutó `ruff check .` en este entorno porque el binario/módulo `ruff` no está disponible localmente y el entorno no tiene acceso de red para resolverlo. La certificación RED oficial debe ejecutarse localmente con las herramientas del proyecto antes del GREEN.
