# ROBY XI.2 — CAP-11 Governed Horizon Generalization
## Reconciliación quirúrgica: Episode budget/step model + checkpoint continuity

Baseline de entrada certificada por el usuario: **13.669 PASS + Ruff limpio**.

## 1. Objetivo estricto del bloque

Generalizar la **constitución del horizonte** de CAP-11 sin abrir todavía un tercer ciclo productivo.

Este bloque NO implementa R3/P3/A3/E3. Su propósito es hacer que el owner canónico de episodio y el carrier de continuidad puedan representar de forma gobernada un episodio con presupuesto finito mayor que dos, manteniendo compatibilidad exacta con el episodio histórico de dos adquisiciones.

La secuencia productiva de dos adquisiciones ya está cerrada y no se reabre:

`R1 → P1 → A1 → E1 → RR1 → R2 → P2 → A2 → E2 → RR2 → CLOSED`

## 2. Owners que deben permanecer únicos

### Episode / budget / stopping
Owner existente y único:

`app.governed_multistep_investigation_episode.GovernedMultiStepInvestigationEpisodeBoundaryV1`

No crear `EpisodeBoundaryV2`, `HorizonManager`, `ResearchLoop`, scheduler ni agente paralelo.

### Continuidad temporal
Carrier/adaptador existente:

`app.governed_long_horizon_investigation_continuity.GovernedLongHorizonInvestigationContinuityV1`

El checkpoint sigue siendo pasivo, read-only y sin auto-persistencia.

### Planning / Authorization / Execution / Reasoning
No se modifican en este bloque. Siguen siendo las autoridades históricas. Un presupuesto mayor **no autoriza** planificación, ejecución ni razonamiento por sí mismo.

## 3. Límite estructural encontrado

### 3.1 Episode state

`GovernedInvestigationEpisodeState` contiene hoy:

- `max_acquisitions: int = 2`;
- rechazo explícito de cualquier valor distinto de 2;
- `current_step` limitado a `{1, 2}`.

Por tanto, el owner canónico ya posee el concepto correcto de presupuesto, pero su dominio está fijado artificialmente a dos.

### 3.2 Episode transitions

La lógica de transición ya es parcialmente genérica:

- `remaining_acquisitions = max_acquisitions - consumed_acquisitions`;
- `record_acquisition` consume una unidad de presupuesto;
- `record_reentry` cierra cuando `consumed_acquisitions == max_acquisitions`.

Sin embargo conserva lenguaje y guardas especializados:

- `second_reentry_closes_fixed_budget_episode`;
- `evaluate_continuation` exige exactamente `remaining_acquisitions == 1`;
- una nueva requirement fuerza `current_step=2`.

### 3.3 Checkpoint

`GovernedPassiveInvestigationCheckpoint` ya transporta `max_acquisitions`, pero:

- rechaza cualquier `max_acquisitions != 2`;
- no transporta `current_step` explícitamente;
- su schema se define como preservación del short-horizon budget.

Para un historial N-step, `current_step` no debe reconstruirse de manera implícita o heurística.

### 3.4 Resume

`GovernedLongHorizonInvestigationContinuityV1.resume(...)` ya contiene la regla adecuada de presupuesto:

`consumed_acquisitions >= max_acquisitions → BUDGET_REVIEW_REQUIRED`

Esa regla es conceptualmente N-step y debe conservarse.

`GovernedLongHorizonInvestigationResumeAdmissionV1` también compara consumo con `checkpoint.max_acquisitions`, por lo que no necesita una segunda autoridad de budget.

## 4. Dictamen de autoridad del budget

No existe en el proyecto una autoridad canónica separada que conceda “horizon budget”. Crear una ahora duplicaría gobierno.

La reconciliación congela esta separación:

- **el Episode Boundary es dueño de representar y hacer cumplir el budget**;
- el budget es un límite constitucional del episodio, no un permiso de ejecución;
- Planning/Authorization/Execution conservan todos sus gates por cada adquisición;
- ampliar `max_acquisitions` nunca equivale a `planning_execution_authorized=True` ni a autorización automática.

Para preservar compatibilidad, el presupuesto histórico por defecto debe seguir siendo **2**.

### Decisión todavía no inventada

El código/documentación actual no contiene una política certificada que determine un hard-cap numérico mayor que 2. Por tanto, esta reconciliación **no inventa un valor máximo arbitrario**.

El RED siguiente debe exigir que todo presupuesto generalizado sea:

- explícito;
- entero positivo;
- finito;
- inmutable durante la vida del episodio;
- sujeto a una cota constitucional declarada antes del GREEN.

La selección concreta de esa cota debe quedar documentada y testeada en el contrato RED, no aparecer implícitamente dentro del GREEN.

## 5. Modelo N-step mínimo correcto

La generalización puede conservar `current_step: int`; no hace falta introducir una nueva colección de objetos Step.

Invariantes mínimas:

1. `1 <= current_step <= max_acquisitions`.
2. `len(requirement_ids) == current_step` para estados activos normales.
3. `consumed_acquisitions == len(execution_ids)`.
4. `len(plan_ids) == len(execution_ids)`.
5. `len(authorization_ids) == len(execution_ids)`.
6. `len(reentry_ids) <= len(execution_ids)`.
7. Todo requirement/plan/authorization/execution/reentry ID permanece único.
8. `remaining_acquisitions == max_acquisitions - consumed_acquisitions`.
9. El budget no puede crecer o reducirse mediante checkpoint/resume.
10. `source_reference` y `world_snapshot_id` siguen siendo lineage canónico del episodio actual.

Invariantes de fase útiles para el RED:

- `OPEN`: step 1, requirement R1 presente, sin adquisición consumida.
- `AWAITING_REENTRY`: la adquisición del `current_step` ya fue registrada y falta su reentry.
- `AWAITING_REQUIREMENT`: acquisition + reentry del `current_step` ya están registrados; sólo puede evaluarse una nueva requirement o stop.
- `READY_FOR_PLANNING`: existe exactamente la nueva requirement del siguiente step, pero esa adquisición aún no fue consumida.
- `CLOSED`: no admite nueva transición productiva.

## 6. Generalización quirúrgica de las transiciones del Episode owner

### `start(...)`

Debe mantener comportamiento histórico por defecto (`max_acquisitions=2`) y, en la futura generalización, aceptar un presupuesto explícito validado sin conceder autoridad operativa.

El `episode_id` debe incorporar el budget explícito en el fingerprint sólo si hacerlo no rompe la compatibilidad de identidad para llamadas históricas sin argumento. La compatibilidad de IDs de episodios existentes debe ser un test RED explícito.

### `record_acquisition(...)`

Ya consume presupuesto de manera general. No necesita semántica P3 específica.

Debe seguir cerrando/fail-closed si no hay budget restante y seguir rechazando reuse/mismatch de lineage.

### `record_reentry(...)`

La regla correcta general es:

- si `consumed_acquisitions == max_acquisitions`: `STOP_REQUIRED + CLOSED + BUDGET_EXHAUSTED`;
- si queda presupuesto: `CONTINUE_ALLOWED + AWAITING_REQUIREMENT`.

Debe eliminarse únicamente la semántica textual especializada en “second reentry”; no debe añadirse una RR3 aquí.

### `evaluate_continuation(...)`

La especialización actual `remaining_acquisitions == 1` es el principal bloqueo productivo del owner.

La regla general debe ser:

- si no queda presupuesto: cierre `BUDGET_EXHAUSTED`;
- si `requirement is None`: cierre `NO_NEW_REQUIREMENT`;
- si requirement reutilizada o con lineage inválido: review fail-closed;
- si requirement nueva y queda budget: append exacto y `current_step += 1`, entrando en `READY_FOR_PLANNING`.

Esto generaliza el owner de estado sin invocar Planning.

## 7. Generalización quirúrgica del checkpoint

`GovernedPassiveInvestigationCheckpoint` debe seguir siendo un carrier pasivo y durable, pero debe transportar suficiente estado constitucional para reconstrucción exacta:

- `max_acquisitions` exacto;
- `current_step` exacto;
- `consumed_acquisitions` exacto;
- lineages completos de requirement/plan/authorization/execution/reentry;
- episode status + stopping reason;
- source/snapshot lineage.

`current_step` debe entrar en el fingerprint del checkpoint.

El checkpoint no puede:

- alterar budget;
- incrementar step;
- crear requirement;
- planificar;
- autorizar;
- ejecutar;
- razonar;
- persistirse a sí mismo;
- iniciar background.

## 8. Resume continuity N-step

`resume(...)` debe seguir siendo consultativo.

Para un checkpoint no agotado y con mismo source/snapshot puede producir `RESUME_CANDIDATE` independientemente de que el step sea 1, 2 o N.

Si `consumed_acquisitions >= max_acquisitions`, debe seguir produciendo `BUDGET_REVIEW_REQUIRED`; resume no puede ampliar el budget histórico.

Cambio de snapshot sigue requiriendo review. Este bloque no generaliza todavía políticas de migración entre snapshots.

## 9. Compatibilidad retroactiva obligatoria

El episodio histórico de dos adquisiciones debe conservarse sin cambios observables para los consumidores existentes:

- `start(...)` sin budget explícito → max 2;
- R1/E1/RR1/R2/E2/RR2 conserva sus estados históricos;
- RR2 sigue cerrando por `BUDGET_EXHAUSTED`;
- checkpoint antiguo de budget 2 sigue válido;
- resume bounded sigue produciendo las mismas clasificaciones;
- P2/A2/E2/RR2 especializados continúan funcionando y no deben generalizarse en este bloque.

## 10. Downstream blockers encontrados — NO modificar todavía

La generalización constitucional no hace por sí sola productivo el step 3+. Permanecen especializaciones explícitas que deberán reconciliarse después:

- `GovernedMultiStepInvestigationProductiveContinuationV1`: sólo declara elegible Planning en step 2 / remaining 1.
- `GovernedMultiStepInvestigationPlanningReentryV1`: sólo admite step 2 / remaining 1.
- `GovernedMultiStepInvestigationAuthorizationReentryV1`: especializado a step 2.
- `GovernedMultiStepInvestigationExecutionReentryV1`: especializado a E2.
- `GovernedMultiStepInvestigationReasoningClosureV1`: terminal RR2 fixed-budget.
- bridges long-horizon P2/A2/E2/RR2: intencionalmente especializados al ciclo certificado.
- `GovernedLongHorizonInvestigationEpisodeEvidenceAdmissionV1`: sólo proyecta estados pre-acquisition step 1 / step 2 desde checkpoint.
- `governed_level2b_productive_entry.py`: exige todavía `max_acquisitions == 2`.

Estos NO son defectos del presente bloque. Son fronteras posteriores del productive continuation N-step.

## 11. Superficie exacta propuesta para el próximo RED

Producción a modificar posteriormente, y sólo después del RED:

1. `app/governed_multistep_investigation_episode.py`
2. `app/governed_long_horizon_investigation_continuity.py`

Compatibilidad a observar, sin generalizar aún:

3. `app/governed_long_horizon_investigation_resume_admission.py`
4. consumidores históricos P2/A2/E2/RR2.

Nuevo contrato RED recomendado:

`tests/architecture/test_cap11_governed_horizon_episode_checkpoint_generalization_contract_red.py`

El RED debe fallar sólo por las limitaciones hardcoded actuales y debe certificar que no aparece una nueva authority.

## 12. Casos RED mínimos

1. Budget histórico por defecto sigue siendo 2.
2. Budget explícito válido >2 puede representarse sólo tras generalización.
3. Budget inválido (0, negativo, no permitido por hard-cap) falla cerrado.
4. `current_step` puede representar N sin exceder budget.
5. Después de una reentry no terminal con budget restante, el owner entra en `AWAITING_REQUIREMENT`.
6. Una nueva requirement válida incrementa step exactamente en uno y entra en `READY_FOR_PLANNING`.
7. La reentry que consume la última adquisición cierra por `BUDGET_EXHAUSTED` sin crear siguiente step.
8. Checkpoint preserva exactos `current_step` y `max_acquisitions`.
9. Checkpoint/resume no altera budget ni lineages.
10. Resume agotado exige `BUDGET_REVIEW_REQUIRED`.
11. Default two-step end-to-end continúa idéntico.
12. No aparece `EpisodeBoundaryV2`, planner/executor/reasoner nuevo, retry ni background.

## 13. Qué NO debe hacer el GREEN de este bloque

- No implementar P3/A3/E3/RR3.
- No tocar `GovernedMultiStepInvestigationReasoningClosureV1` para “que deje de cerrar”.
- No cambiar los bridges P2/A2/E2/RR2 certificados.
- No crear un loop automático.
- No convertir budget en permiso de ejecución.
- No introducir persistencia o scheduler.
- No modificar Memory ni World Model.
- No elegir silenciosamente un hard-cap sin contrato RED.

## 14. Residual después de este bloque

Una vez generalizados Episode + Checkpoint, el siguiente residual quedará claramente separado:

**N-step Productive Continuation Reconciliation**

`AWAITING_REQUIREMENT(step k, budget remaining) → exact governed R(k+1) → existing Planning → existing Authorization → existing Execution → existing Reasoning re-entry`

Ese bloque deberá decidir cómo reutilizar los owners especializados actuales sin clonar P3/A3/E3 y sin romper el circuito histórico de dos adquisiciones.

## 15. Dictamen final

La arquitectura correcta no consiste en añadir un tercer paso manual. Consiste en hacer que el **mismo Episode owner** pueda representar y gobernar un horizonte finito N-step, mientras el **mismo checkpoint** conserva exactamente ese estado a través de pausas y resumes.

La reconciliación determina que sólo dos piezas constitutivas necesitan generalización inmediata: **Episode budget/step model** y **checkpoint continuity**. El resto de la cadena productiva debe permanecer congelado hasta el bloque posterior.
