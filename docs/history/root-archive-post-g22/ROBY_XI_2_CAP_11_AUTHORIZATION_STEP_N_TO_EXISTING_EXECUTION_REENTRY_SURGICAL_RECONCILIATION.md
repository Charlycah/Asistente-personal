# CAP-11 — Authorization step N → existing Execution re-entry — Reconciliación quirúrgica

Estado de entrada: baseline productiva certificada **13.694 PASS + Ruff limpio**.

## 1. Dictamen

No hace falta un nuevo executor, gateway, scheduler, research loop ni autoridad paralela.
La autoridad productiva correcta ya existe en:

- `app.governed_multistep_investigation_execution_reentry.GovernedMultiStepInvestigationExecutionReentryV1`
- `app.governed_level2_read_only_execution_gateway.GovernedLevel2ReadOnlyExecutionGatewayV1`
- `app.runtime_capability_registry.OfficialRuntimeCapabilityRegistry`
- `app.governed_multistep_investigation_episode.GovernedMultiStepInvestigationEpisodeBoundaryV1.record_acquisition(...)`

El owner existente ya realiza exactamente la secuencia constitucional requerida: valida Authorization, invoca una sola vez el gateway existente, valida lineage del envelope, rechaza reuse de execution id y registra la adquisición por el Episode owner.

## 2. Residual real encontrado

El owner sigue codificado semánticamente como E2 terminal. El bloqueo no son sólo dos guards de admisión; existen cinco supuestos históricos que impiden step N:

1. `_eligibility_error(...)` exige `current_step == 2`.
2. `_eligibility_error(...)` exige `remaining_acquisitions == 1` antes de ejecutar.
3. El camino ACQUIRED exige que después de `record_acquisition(...)` `remaining_acquisitions == 0`.
4. `GovernedInvestigationExecutionReentryResult.__post_init__` exige remaining zero para cualquier resultado ACQUIRED.
5. `eligible_for_reasoning_reentry` sólo puede ser verdadero cuando remaining zero.

Los puntos 3–5 son incompatibles con una adquisición step 3 dentro de budget 4: después de registrar E3 el Episode queda correctamente `AWAITING_REENTRY` con una adquisición todavía disponible. Esa evidencia debe poder volver a Reasoning antes de decidir si existe un requirement siguiente.

## 3. Invariante N-step congelado para admisión a Execution

Un `GovernedInvestigationAuthorizationReentryResult` puede entrar al owner existente únicamente si conserva simultáneamente:

- `status == AUTHORIZED`;
- `eligible_for_existing_execution == True`;
- exactamente una invocación de Authorization;
- `authorization_product` y `planning_product` presentes;
- Episode state `READY_FOR_PLANNING`;
- `2 <= current_step <= max_acquisitions`;
- `consumed_acquisitions == current_step - 1`;
- `remaining_acquisitions > 0` antes de ejecutar;
- exact episode / requirement / plan / authorization / source / snapshot lineage;
- `execution_authorized == False` como límite no-ejecutivo previo.

No se introduce una segunda decisión de presupuesto: el budget sigue siendo propiedad del Episode Boundary.

## 4. Invariante N-step después de una adquisición ACQUIRED

El gateway existente se invoca como máximo una vez. Si retorna `ACQUIRED` y el lineage es válido, `record_acquisition(...)` debe ser invocado exactamente una vez.

El resultado productivo correcto después del record es:

- `status == ACQUIRED`;
- exact `GovernedAcquiredEvidenceEnvelope` preservado;
- execution id nuevo respecto del Episode previo;
- resulting Episode state `AWAITING_REENTRY`;
- `consumed_acquisitions` incrementado exactamente en uno;
- `remaining_acquisitions == max_acquisitions - consumed_acquisitions`, pudiendo ser mayor que cero;
- `eligible_for_reasoning_reentry == True` para toda adquisición ACQUIRED correctamente registrada y en `AWAITING_REENTRY`.

La elegibilidad de Reasoning no significa invocarlo. Es sólo la frontera declarativa del siguiente owner.

## 5. Compatibilidad histórica P2/A2/E2

El caso histórico budget 2 permanece exactamente válido:

- antes de E2: step 2, consumed 1, remaining 1;
- después de E2: consumed 2, remaining 0, `AWAITING_REENTRY`;
- `eligible_for_reasoning_reentry == True`;
- execution, authorization, plan, requirement, source y snapshot lineage intactos.

No es necesario cambiar ids, fingerprints ni rationale históricos observables cuando se pueda evitar. La generalización debe ser estructural y no reescribir compatibilidad certificada sin necesidad.

## 6. STOP line

Este bloque debe terminar inmediatamente después de producir el exacto `GovernedInvestigationExecutionReentryResult` y registrar la adquisición en Episode.

Puede exponer `eligible_for_reasoning_reentry=True` cuando la adquisición fue ACQUIRED y el Episode quedó `AWAITING_REENTRY`.

No puede:

- invocar `GovernedLevel2ReasoningReentryFoundationV1`;
- producir RR3/RR4;
- evaluar un requirement siguiente;
- invocar Planning o Authorization otra vez;
- hacer retry de Execution;
- extender budget;
- crear scheduler, loop, manager o segundo executor;
- tocar Memory / World Model / conversation / background work.

## 7. Bridge histórico E2

`app/governed_long_horizon_investigation_e2_execution_reentry.py` sigue siendo un bridge histórico A2→E2 del episodio de dos adquisiciones. Contiene guards deliberados step 2 / remaining 1 y validación terminal remaining 0.

**No debe generalizarse en este bloque.**

El camino N-step constitucional es directamente:

`GovernedInvestigationAuthorizationReentryResult`
→ `GovernedMultiStepInvestigationExecutionReentryV1`
→ existing Level2 read-only Execution gateway
→ `EpisodeBoundary.record_acquisition(...)`.

Si más adelante se necesita wiring long-horizon genérico para E3/E4, deberá reconciliarse como una capa de wiring separada que consuma este owner ya generalizado, nunca como otro executor.

## 8. Fail-closed preservado

Deben seguir cerrando sin retry:

- Authorization no elegible;
- lineage roto;
- reused execution id;
- gateway exception;
- envelope DENIED / REVIEW_REQUIRED;
- acquisition UNAVAILABLE / FAILED;
- Episode que rechaza el record.

La generalización N-step no relaja ninguna política de seguridad ni añade automatización.

## 9. RED recomendado

El siguiente RED contractual debe congelar, como mínimo:

- A3/budget 4 entra al existing Execution owner exactamente una vez;
- E3 se registra exactamente una vez y queda `AWAITING_REENTRY` con remaining 1;
- E3 es elegible para existing Reasoning re-entry aunque el budget no esté agotado;
- A4/budget 4 produce E4, remaining 0 y la misma elegibilidad declarativa;
- E3/E4 preservan exact Rn/Pn/An/source/snapshot lineage y execution id nuevo;
- el caso histórico A2/E2 budget 2 sigue idéntico;
- se retiran los guards terminales step-2/remaining-zero del owner canónico;
- no se invoca Reasoning;
- no se modifica el bridge histórico E2;
- no aparece ningún nuevo executor/gateway/loop/manager.

## 10. Dictamen final

**No falta una nueva capacidad de Execution. Falta generalizar el owner existente desde “E2 terminal” a “una adquisición autorizada step N”.**

El cambio GREEN futuro debe ser local al owner canónico de Execution y sus contratos, conservando el gateway y el Episode Boundary existentes. La frontera termina antes de Reasoning re-entry.
