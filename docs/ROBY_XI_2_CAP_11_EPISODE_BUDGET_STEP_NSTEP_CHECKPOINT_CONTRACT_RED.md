# ROBY XI.2 — CAP-11 Governed Horizon Generalization
## RED contractual: Episode budget/step N-step + checkpoint continuity

Baseline de entrada certificada: **13.669 PASS + Ruff limpio**.

## 1. Alcance estricto

Este RED congela exclusivamente la constitución N-step del owner de episodio y del carrier pasivo de continuidad. No hace productivo step 3+, no crea R3/P3/A3/E3 y no modifica Planning, Authorization, Execution ni Reasoning.

Owners preservados:

- Episode/budget/stopping: `GovernedMultiStepInvestigationEpisodeBoundaryV1`.
- Continuidad pasiva: `GovernedLongHorizonInvestigationContinuityV1`.

## 2. Política constitucional de budget congelada

El presupuesto histórico por defecto permanece en **2 adquisiciones**.

La primera generalización gobernada admite un budget explícito entero en el rango inclusivo **1..4**. Se congela:

`GOVERNED_INVESTIGATION_MAX_ACQUISITIONS = 4`

La cota 4 es deliberadamente conservadora: es la mínima extensión acotada que permite demostrar continuidad real más allá del ciclo de dos adquisiciones sin convertir el budget en un loop abierto. Cambiar esta cota en el futuro requiere una modificación gobernada separada; no puede crecer por checkpoint, resume, Planning ni autorización.

El budget:

- es finito e inmutable durante el episodio;
- no concede autoridad operativa;
- no autoriza Planning/Execution;
- no puede ampliarse mediante resume;
- falla cerrado si está fuera de `1..4` o no es un entero válido.

## 3. Contrato N-step del Episode state

Debe poder representar estados con:

- `1 <= current_step <= max_acquisitions <= 4`;
- `len(requirement_ids) == current_step` en estados activos normales;
- `consumed_acquisitions == len(execution_ids)`;
- `len(plan_ids) == len(execution_ids)`;
- `len(authorization_ids) == len(execution_ids)`;
- `len(reentry_ids) <= len(execution_ids)`;
- IDs únicos en cada lineage;
- `remaining_acquisitions == max_acquisitions - consumed_acquisitions`.

El default histórico debe continuar siendo `max_acquisitions=2`.

## 4. `start(...)`

El owner existente debe aceptar `max_acquisitions` keyword-only con default `2`.

Compatibilidad de identidad:

- llamada histórica sin argumento conserva exactamente el episode ID preexistente;
- `max_acquisitions=2` explícito produce el mismo ID histórico;
- un budget distinto debe participar en la identidad para evitar colisión entre episodios con igual lineage y distinta constitución.

`start(...)` no concede ninguna autoridad adicional.

## 5. Reentry y continuación genéricas

`record_reentry(...)`:

- si `consumed_acquisitions == max_acquisitions` → `STOP_REQUIRED + CLOSED + BUDGET_EXHAUSTED`;
- si queda budget → `CONTINUE_ALLOWED + AWAITING_REQUIREMENT`;
- no existe semántica especial de “second reentry” en la constitución generalizada.

`evaluate_continuation(...)`:

- sin budget → cierre `BUDGET_EXHAUSTED`;
- `requirement is None` → cierre `NO_NEW_REQUIREMENT`;
- requirement reutilizada / source mismatch / snapshot mismatch → fail-closed;
- requirement nueva con budget → append exacto, `current_step += 1`, `READY_FOR_PLANNING`;
- no invoca Planning.

## 6. Checkpoint continuity

`GovernedPassiveInvestigationCheckpoint` debe transportar explícitamente:

- `current_step` exacto;
- `max_acquisitions` exacto;
- `consumed_acquisitions` exacto;
- todos los lineages existentes;
- status/stopping/source/snapshot.

El `current_step` debe participar en el fingerprint del checkpoint.

El checkpoint mantiene carácter pasivo, read-only y sin autoridad.

## 7. Resume N-step

Para un checkpoint con budget no agotado, source y snapshot compatibles, `resume(...)` puede producir `RESUME_CANDIDATE` aunque `current_step > 2`.

Si `consumed_acquisitions >= max_acquisitions`, conserva `BUDGET_REVIEW_REQUIRED` y nunca amplía el budget.

## 8. Compatibilidad obligatoria

El ciclo histórico de dos adquisiciones debe permanecer observablemente intacto:

- default 2;
- episode ID histórico sin argumento intacto;
- RR2 agota y cierra;
- checkpoints creados por el owner histórico bounded siguen clasificándose igual;
- consumidores P2/A2/E2/RR2 no se generalizan en este bloque.

## 9. Prohibiciones del GREEN posterior

Este contrato NO autoriza:

- `EpisodeBoundaryV2`;
- Horizon manager / research loop / scheduler;
- P3/A3/E3/RR3 productivos;
- nuevo planner/executor/reasoner;
- autorización automática por disponer de budget;
- persistencia, Memory/World Model write, background o retry.

## 10. Criterio RED esperado

Contra la producción actual, deben fallar únicamente las expectativas nuevas de generalización: hard-cap declarado, `start(max_acquisitions=...)`, estado step 3+, continuación step 2→3, checkpoint con `current_step` y resume N-step. Los contratos históricos de budget 2 deben seguir pasando.
