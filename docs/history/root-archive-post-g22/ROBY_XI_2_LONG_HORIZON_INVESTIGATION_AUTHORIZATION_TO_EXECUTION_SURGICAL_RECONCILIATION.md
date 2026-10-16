# ROBY XI.2 — Long-horizon Investigation
## Reconciliación quirúrgica — Existing Governed Authorization → Existing Governed Execution Gateway

**Baseline oficial de entrada:** 13.575 PASS + Ruff limpio.

## Hallazgo

El residual no requiere un nuevo owner de Execution. ROBY XI.2 ya posee el gateway canónico `GovernedLevel2ReadOnlyExecutionGatewayV1`, que ejecuta una única lectura Level 2 mediante `OfficialRuntimeCapabilityRegistry` y delega finalmente en `OfficialCapabilityGateway`.

El producto certificado del bloque anterior, `GovernedInvestigationEvidenceAuthorizationResult`, conserva por identidad tanto `authorization_product` como `planning_product` y deriva `eligible_for_existing_execution=True` únicamente de una decisión `MAY_INITIATE`.

## Corte productivo exacto

Entrada elegible:

`GovernedInvestigationEvidenceAuthorizationResult`

con:

- status `AUTHORIZED`;
- decision `MAY_INITIATE`;
- `eligible_for_existing_execution=True`;
- authorization product presente;
- planning product presente;
- authorization product con `eligible_for_next_governed_gate=True`;
- independence level `LEVEL_2_READ_ONLY`;
- lineage authorization/requirement/plan/source/snapshot consistente;
- estado no pre-autorizado para ejecución.

Delegación única:

`GovernedLevel2ReadOnlyExecutionGatewayV1.execute(authorization_product, planning_product, now=now)`

El adapter long-horizon no reconstruye autorización ni planning, no selecciona otra capability y no implementa un executor propio.

## Owner

La cadena de ejecución permanece:

`GovernedLevel2ReadOnlyExecutionGatewayV1`
→ `OfficialRuntimeCapabilityRegistry`
→ `OfficialCapabilityGateway`

No se crea una autoridad paralela.

## Compatibilidad Level 2

`MAY_INITIATE` es condición necesaria pero no suficiente para este gateway. Una autorización `LEVEL_1_CONVERSATIONAL`, aunque sea `MAY_INITIATE`, no debe invocar el gateway Level 2. Debe cerrar con cero ejecuciones.

Esta comprobación no recalcula Authorization: sólo verifica compatibilidad con el gateway canónico elegido.

## Prohibición de atajo histórico

No reutilizar `GovernedMultiStepInvestigationExecutionReentryV1`: contiene invariantes de continuación multi-step (`current_step == 2`, budget restante, record de episodio y reasoning reentry) que no pertenecen a este residual.

## Semántica de ejecución

Cruzar este corte sí puede adquirir una observación real de solo lectura. Debe mantenerse:

- one-shot: como máximo una invocación del execution gateway;
- sin retry;
- sin persistencia automática;
- sin establecer verdad;
- sin modificar memoria ni world model;
- sin reasoning reentry automático;
- sin record de episodio dentro de este bridge.

Los estados canónicos del gateway (`ACQUIRED`, `DENIED`, `UNAVAILABLE`, `FAILED`, `REVIEW_REQUIRED`) deben preservarse, no reinterpretarse como nueva autorización.

## Corte de salida

El bloque termina al obtener y preservar el `GovernedAcquiredEvidenceEnvelope` emitido por el gateway existente.

No debe registrar todavía esa evidencia en el episodio ni invocar reasoning reentry.

Residual posterior:

`Existing Acquired Evidence Envelope → Governed Episode Evidence Admission / Reasoning Reentry`.
