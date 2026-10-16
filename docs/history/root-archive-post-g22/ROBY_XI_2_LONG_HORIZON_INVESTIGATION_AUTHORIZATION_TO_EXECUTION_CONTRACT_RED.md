# ROBY XI.2 — Long-horizon Investigation
## Contract RED — Existing Governed Authorization → Existing Governed Execution Gateway

**Baseline oficial de entrada:** 13.575 PASS + Ruff limpio.

## 1. Objetivo

Congelar el bridge mínimo desde la autorización existente y elegible hacia el execution gateway Level 2 ya existente, sin crear executor, retry, persistencia, episode recording ni reasoning reentry.

## 2. Módulo contractual esperado

`app.governed_long_horizon_investigation_evidence_execution`

Superficies mínimas esperadas:

- `GovernedInvestigationEvidenceExecutionStatus`
- `GovernedInvestigationEvidenceExecutionResult`
- `GovernedLongHorizonInvestigationEvidenceExecutionV1`
- `consume(authorization_result, *, now)`

## 3. Owner canónico

El módulo nuevo NO es autoridad de Execution.

Debe delegar exclusivamente en:

`GovernedLevel2ReadOnlyExecutionGatewayV1`

que ya utiliza:

`OfficialRuntimeCapabilityRegistry → OfficialCapabilityGateway`.

## 4. Elegibilidad de entrada

Sólo un `GovernedInvestigationEvidenceAuthorizationResult` con:

- status `AUTHORIZED`;
- decision `MAY_INITIATE`;
- `eligible_for_existing_execution=True`;
- authorization product presente;
- planning product presente;
- `authorization_product.eligible_for_next_governed_gate=True`;
- independence level `LEVEL_2_READ_ONLY`;
- lineage consistente;
- `execution_authorized=False`;

puede alcanzar el gateway.

Una autorización Level 1 conversacional no puede alcanzar este gateway aunque su decisión sea `MAY_INITIATE`.

## 5. Productos exactos

Execution debe recibir exactamente:

- `authorization_result.authorization_product`;
- `authorization_result.planning_product`.

Prohibido reconstruir cualquiera de ambos, volver a ejecutar Authorization o Planning, o seleccionar una capability distinta.

## 6. Invocación

El adapter permite como máximo una invocación a `GovernedLevel2ReadOnlyExecutionGatewayV1.execute(...)` por `consume(...)`.

No retry. Una excepción del bridge debe producir cierre fail-closed y nunca una segunda ejecución.

## 7. Lineage de salida

El resultado debe preservar como mínimo:

- admission/thread/checkpoint/resume/episode/reasoning;
- authorization ID;
- requirement ID;
- plan ID;
- source reference;
- world snapshot ID;
- exact authorization product;
- exact planning product;
- exact `GovernedAcquiredEvidenceEnvelope` cuando el gateway fue invocado.

## 8. Estados

El bridge debe distinguir una entrada no elegible de una ejecución efectivamente intentada.

Cuando existe envelope, el estado canónico del gateway debe preservarse: `ACQUIRED`, `DENIED`, `UNAVAILABLE`, `FAILED` o `REVIEW_REQUIRED`.

## 9. Límites

El bridge no puede:

- crear otro executor;
- usar `GovernedMultiStepInvestigationExecutionReentryV1`;
- ejecutar más de una vez;
- hacer retry;
- persistir evidencia;
- establecer verdad;
- registrar la adquisición en el episodio;
- invocar reasoning reentry;
- modificar memoria;
- modificar world model;
- iniciar procesos en background.

## 10. Residual posterior

El GREEN debe detenerse con el envelope de evidencia existente.

Residual posterior:

`Existing Acquired Evidence Envelope → Governed Episode Evidence Admission / Reasoning Reentry`.
