# CAP-11 — RR(N) → requisito discriminante R(N+1) — Reconciliación quirúrgica

Estado: reconciliación cerrada. Sin cambios de producción.

## Límite exacto del bloque

Entrada: resultado gobernado de Reasoning re-entry ya registrado en Episode, con Episode en `AWAITING_REQUIREMENT` y budget restante.

Salida: cero o un requisito discriminante gobernado R(N+1), admitido mediante la autoridad existente de discriminación + continuidad del Episode.

STOP absoluto inmediatamente después de la admisión del requisito. Este bloque no entra en Planning.

## Autoridades canónicas existentes

No se crea una nueva autoridad de requirement.

- Requirement / discriminación: `GovernedMultiHypothesisProductiveConsumptionV1`.
- Requirement canónico: `DiscriminatingEvidenceRequirement`.
- Episode / continuación: `GovernedMultiStepInvestigationProductiveContinuationV1` → `GovernedMultiStepInvestigationEpisodeBoundaryV1.evaluate_continuation(...)`.
- Integración histórica RR1→R2: `GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1`.

## Residual real

La integración histórica RR1→R2 sigue fijada a step 1 / remaining 1 y a `GovernedInvestigationReasoningReentryRecordingResult`.

Los guards específicos encontrados son:
- `state.current_step == 1`;
- `state.remaining_acquisitions == 1`;
- transición válida exige `current_step == 2`;
- transición válida exige `remaining_acquisitions == 1`;
- mensajes y contratos hablan explícitamente de R2.

La autoridad de continuidad ya es N-step y no necesita duplicación.

## Contrato N-step congelado

Un RR(N) puede entrar sólo cuando:
- el Reasoning re-entry existente fue ejecutado exactamente una vez;
- el re-entry fue registrado exactamente una vez en Episode;
- Episode está `AWAITING_REQUIREMENT`;
- `2 <= current_step <= max_acquisitions - 1` para el estado posterior a RR(N);
- `consumed_acquisitions == current_step`;
- `remaining_acquisitions > 0`;
- re-entry, evidence, source, snapshot, episode y revised report conservan lineage exacto;
- no existe requirement nuevo ya admitido para el siguiente step.

La discriminación se invoca exactamente una vez.

Cardinalidad:
- 0 requirements → `STOP_REQUIRED`, Episode `CLOSED`, `NO_NEW_REQUIREMENT`;
- 1 requirement exacto → se admite R(N+1) una sola vez;
- >1 requirements → `REVIEW_REQUIRED`, sin admisión.

Para una admisión válida:
- transición `CONTINUE_ALLOWED`;
- Episode `READY_FOR_PLANNING`;
- `current_step` aumenta exactamente uno;
- `consumed_acquisitions` no cambia;
- budget restante se conserva;
- `current_requirement_id` es exactamente R(N+1);
- la elegibilidad para Planning puede exponerse, pero Planning no se invoca.

Ejemplo budget 4:
- después de RR3: `current_step=3`, consumed=3, remaining=1, `AWAITING_REQUIREMENT`;
- discriminar/admitir R4;
- Episode queda `READY_FOR_PLANNING`, `current_step=4`, consumed=3, remaining=1;
- STOP antes de P4.

## Preservación histórica

RR1→R2 con budget 2 debe seguir exactamente soportado.

No se generaliza ni modifica en este bloque:
- Planning re-entry;
- Authorization re-entry;
- Execution re-entry;
- Reasoning re-entry;
- Episode budget/cap;
- Curiosity;
- Memory / World Model;
- Conversation;
- background work;
- retry;
- budget extension.

## Decisión arquitectónica

El siguiente RED debe generalizar la integración existente de requirement admission sin crear un segundo Requirement owner. El STOP contractual queda después de R(N+1), antes de cualquier Planning.
