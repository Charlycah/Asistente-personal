# ROBY XI.2 — RR1 AWAITING_REQUIREMENT → Governed R2 Requirement Admission
## Reconciliación quirúrgica

**Baseline de entrada:** 13.605 PASS + Ruff limpio, certificada localmente.

## 1. Residual exacto

El GREEN anterior deja RR1 en `GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT`
con una adquisición restante. Ese estado todavía no contiene R2 y no debe inventarlo.

El residual es:

`RR1 recorded continuation`
+ `exact revised GovernedHypothesisDeepeningReport`
→ existing governed multi-hypothesis discrimination
→ zero or one admissible new `DiscriminatingEvidenceRequirement`
→ existing investigation productive continuation
→ `READY_FOR_PLANNING` or governed stop

Planning permanece fuera de este bloque.

## 2. Autoridad canónica de producción del requirement

La única construcción productiva encontrada de `DiscriminatingEvidenceRequirement` está en:

- `core.governed_reasoning.multi_hypothesis_discrimination.GovernedMultiHypothesisDiscriminator`
- expuesta por `app.governed_multi_hypothesis_productive_consumption.GovernedMultiHypothesisProductiveConsumptionV1`

`DiscriminatingEvidenceRequirement` continúa bajo autoridad `governed_reasoning`.
No se crea otro requirement factory, selector, Curiosity owner ni planner.

## 3. Autoridad canónica de admisión al episodio

La admisión del siguiente requirement ya existe en:

- `GovernedMultiStepInvestigationEpisodeBoundaryV1.evaluate_continuation(...)`
- expuesta de forma productiva por
  `GovernedMultiStepInvestigationProductiveContinuationV1.consume(...)`

Ese boundary exige `AWAITING_REQUIREMENT`, una adquisición restante, requirement nuevo,
source exacto y snapshot exacto. En éxito mueve el mismo episodio a
`READY_FOR_PLANNING`, step 2, sin ejecutar Planning.

## 4. Por qué RR1 no puede fabricar R2

`GovernedLevel2ReasoningReentryResult` conserva lineage y un `reasoning_result`, pero no
expone un `GovernedHypothesisDeepeningReport` revisado ni un
`DiscriminatingEvidenceRequirement` productivo. Derivar R2 desde texto, IDs o el resultado
genérico del reentry inventaría semántica cognitiva y crearía una autoridad paralela.

El runtime gobernado ya posee una cadena epistemic/deepening explícita y el proyecto ya
usa `GovernedHypothesisDeepeningReport` como input semántico para discriminación y para
Evidence-driven Explanatory Model Revision. Por ello el próximo bridge debe recibir el
**revised report exacto como input explícito**, no reconstruirlo.

## 5. Evidencia de RR1 debe estar aplicada

Antes de producir R2, el revised report debe:

- preservar `source_reference` y `world_snapshot_id` del episodio/RR1;
- contener el `evidence_id` exacto del reasoning reentry en al menos una assessment;
- permanecer bajo la semántica de hypothesis deepening; no promover observación a verdad.

Sin esa prueba estructural, el bridge falla cerrado antes de admitir un nuevo requirement.

## 6. Cardinalidad gobernada

- **0 requirements:** no se inventa R2. Se entrega `None` al existing productive
  continuation para obtener el stop canónico `NO_NEW_REQUIREMENT`.
- **1 requirement:** se preserva el objeto exacto y se entrega una sola vez al existing
  productive continuation.
- **>1 requirements:** `REVIEW_REQUIRED`; no selección arbitraria, ranking ni Curiosity.

Un requirement cuyo ID ya exista en el episodio, o con lineage source/snapshot distinto,
será rechazado por el boundary existente.

## 7. Corte productivo congelado

Nuevo adapter mínimo recomendado:

`app.governed_long_horizon_investigation_reassessment_requirement_admission`

Contrato público previsto:

- `GovernedInvestigationReassessmentRequirementAdmissionStatus`
- `GovernedInvestigationReassessmentRequirementAdmissionResult`
- `GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1`

Input:

- exact `GovernedInvestigationReasoningReentryRecordingResult` de RR1;
- exact revised `GovernedHypothesisDeepeningReport`.

Delegaciones máximas:

1. `GovernedMultiHypothesisProductiveConsumptionV1.consume(revised_report)` una vez;
2. `GovernedMultiStepInvestigationProductiveContinuationV1.consume(state, requirement)`
   una vez cuando cardinalidad sea 0 o 1.

Salida de éxito R2:

- exact requirement object;
- exact productive continuation;
- same episode/thread/checkpoint/reentry lineage;
- `READY_FOR_PLANNING`, `current_step == 2`, `remaining_acquisitions == 1`;
- `eligible_for_existing_planning=True`;
- STOP.

Salida sin nuevo requirement:

- exact governed continuation stop;
- `CLOSED + NO_NEW_REQUIREMENT`;
- no Planning eligibility.

## 8. Prohibiciones del bloque

El adapter no puede:

- inventar/rewrite R2;
- elegir arbitrariamente entre múltiples requirements;
- reconstruir hypothesis semantics desde IDs;
- llamar Planning, Authorization, Execution o Reasoning;
- reintentar adquisición;
- crear Curiosity questions;
- persistir resultados;
- modificar Memory o World Model;
- establecer verdad/causalidad;
- iniciar procesos de fondo.

## 9. Decisión

El próximo RED debe congelar **RR1 reassessment → exact governed R2 requirement admission**.
No debe congelar todavía R2 → Planning, porque esa superficie ya tiene owner histórico y
se conectará sólo después de certificar este límite.
