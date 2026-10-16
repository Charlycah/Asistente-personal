# ROBY XI.2 — CAP-11 Planning step N → Existing Authorization re-entry — Reconciliación quirúrgica

## 1. Baseline de entrada

Baseline productiva certificada por el usuario: **13.689 PASS + Ruff limpio**.

Este corte es exclusivamente de reconciliación. No generaliza producción todavía.

## 2. Autoridad canónica

No falta una nueva capacidad de Authorization. La autoridad existente y única sigue siendo:

`GovernedMultiStepInvestigationAuthorizationReentryV1`
→ `GovernedIndependenceAuthorizationBoundaryV1`
→ `GovernedIndependenceAuthorizationProductiveConsumptionV1`.

No se crea `V2`, AuthorizationManager, scheduler, loop, bridge N-step paralelo ni segunda autoridad.

## 3. Entrada ya certificada

El bloque anterior dejó certificado el owner canónico de Planning para step N:

`GovernedMultiStepInvestigationPlanningReentryV1`

Un resultado productivo conserva:

- `status = PLANNED`;
- exact `planning_product`;
- exact requirement/plan/source/snapshot lineage;
- exact `current_step` y `remaining_acquisitions`;
- `eligible_for_authorization=True` sólo cuando el Planning canónico es `PLANNABLE`;
- cero invocaciones de Authorization/Execution/Reasoning.

Por tanto el input correcto del presente bloque ya existe: el exacto
`GovernedInvestigationPlanningReentryResult` step N.

## 4. Residual real encontrado

`GovernedMultiStepInvestigationAuthorizationReentryV1` ya es signature-compatible con el
resultado Planning N-step. Su `consume(...)` ya:

1. recibe `GovernedInvestigationPlanningReentryResult`;
2. valida elegibilidad antes de Authorization;
3. llama una sola vez a `GovernedIndependenceAuthorizationBoundaryV1.evaluate(...)`;
4. consume el report por la superficie productiva existente;
5. valida requirement/plan/source/snapshot lineage;
6. rechaza reutilización de authorization IDs previos;
7. preserva el exacto producto de Authorization;
8. deriva Execution eligibility únicamente de `MAY_INITIATE`;
9. no ejecuta capabilities ni Reasoning ni modifica Episode state.

El bloqueo N-step es local y explícito en `_eligibility_error(...)`:

- `planning_reentry.current_step != 2` → `step_two_required`;
- `planning_reentry.remaining_acquisitions != 1` → `single_remaining_budget_required`.

También permanecen nombres/rationales históricos P2/A2 (`planned_p2_required`,
`p2_not_authorization_eligible`, `plannable_p2_required`, `non_executive_p2_required`,
`new_a2_from_existing_authority`). Son vocabulario histórico, no una autoridad distinta,
pero el GREEN N-step debería reemplazar los guards semánticos step-2 por invariantes N-step
sin romper el caso histórico.

## 5. Generalización mínima correcta

La elegibilidad Authorization step N debe derivarse del Planning ya certificado y de su
Episode lineage, no de números mágicos de step 2:

- `status is PLANNED`;
- `eligible_for_authorization is True`;
- `planning_status is PLANNABLE`;
- `planning_product is not None`;
- `2 <= current_step <= resulting_state.max_acquisitions`;
- `resulting_state.consumed_acquisitions == current_step - 1`;
- `remaining_acquisitions > 0`;
- exact requirement ID == current Episode requirement;
- exact plan ID == Planning product plan;
- exact source/snapshot lineage;
- no execution authorization or side effect has ocurrido.

El owner Authorization debe seguir recibiendo exactamente el mismo tipo y debe invocar la
misma autoridad existente exactamente una vez.

## 6. Compatibilidad histórica obligatoria

El caso histórico step 2 / budget 2 debe seguir funcionando exactamente:

R2 → P2 `PLANNED/PLANNABLE` → existing Authorization owner → A2 product.

No se modifica ni generaliza el bridge histórico
`governed_long_horizon_investigation_a2_authorization_reentry.py`; sigue siendo un bridge
P2→A2 de compatibilidad histórica.

El camino N-step de este corte es directamente:

`GovernedMultiStepInvestigationPlanningReentryV1`
→ `GovernedMultiStepInvestigationAuthorizationReentryV1`
→ existing Independence Authorization authority.

## 7. Semántica del resultado N-step

Para un P3/P4 válido, el mismo `GovernedInvestigationAuthorizationReentryResult` debe poder
representar:

- `status = AUTHORIZED` cuando la autoridad existente produce un producto válido;
- exact `authorization_product`;
- nuevo authorization ID no presente en el Episode lineage previo;
- exact requirement/plan/source/snapshot;
- exact `current_step` y budget sin mutarlos;
- exact `decision`;
- `eligible_for_existing_execution=True` sólo para `MAY_INITIATE`.

`MUST_ASK` y `MUST_ABSTAIN` siguen siendo resultados Authorization válidos pero no Execution-eligible.

## 8. STOP absoluto antes de Execution

Este bloque puede exponer Execution eligibility, pero no puede ejecutar.

Queda prohibido:

- invocar `GovernedMultiStepInvestigationExecutionReentryV1`;
- invocar `GovernedLevel2ReadOnlyExecutionGatewayV1`;
- producir E3/E4;
- llamar `record_acquisition`;
- invocar Reasoning re-entry;
- crear otro requirement o plan;
- incrementar step o budget;
- modificar Episode state;
- persistir;
- tocar Memory/World Model;
- iniciar background work;
- retry automático.

## 9. Fail-closed

Debe ser `NOT_ELIGIBLE` con cero llamadas a Authorization si Planning no es `PLANNED`, no es
`PLANNABLE`, no es Authorization-eligible, falta producto, el step/budget no está alineado o
la lineage de requirement/plan/source/snapshot es inconsistente.

Si la única llamada a Authorization falla, el resultado sigue siendo `REVIEW_REQUIRED`, sin
retry. Si el report/producto devuelve lineage incorrecto o reutiliza una Authorization
previa, también es `REVIEW_REQUIRED`.

## 10. RED recomendado

El RED contractual siguiente debe congelar como mínimo:

- P3 / budget 4 entra al owner Authorization existente exactamente una vez;
- P4 / budget 4 también es Authorization-eligible cuando consumed=3;
- exact R3/P3 y R4/P4 se preservan;
- A3/A4 son nuevos respecto de authorization IDs previos;
- `MAY_INITIATE` sólo expone `eligible_for_existing_execution=True`;
- `MUST_ASK` / `MUST_ABSTAIN` no exponen Execution eligibility;
- step/budget incoherente falla antes de Authorization;
- caso histórico step 2 / budget 2 permanece certificado;
- desaparecen los guards productivos `current_step != 2` y `remaining_acquisitions != 1`;
- no se crea ninguna autoridad Authorization nueva;
- STOP antes de Execution.

## 11. Dictamen

**No falta Authorization N-step. Falta retirar dos guards históricos step-2 del owner
canónico ya correcto y reemplazarlos por la alineación N-step certificada.**

El próximo bloque debe ser RED contractual. Execution N-step queda expresamente cerrado
hasta su propia reconciliación posterior.
