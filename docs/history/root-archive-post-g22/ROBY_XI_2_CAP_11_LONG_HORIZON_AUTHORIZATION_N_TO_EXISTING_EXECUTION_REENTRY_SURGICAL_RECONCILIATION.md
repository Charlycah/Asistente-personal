# ROBY XI.2 — CAP-11 — Long-horizon Authorization N → existing Execution re-entry — Reconciliación quirúrgica

## Baseline oficial de entrada

**13.715 PASS + Ruff limpio**, certificada localmente por el usuario.

Naturaleza del corte: **reconciliación únicamente**. No se modifica producción, no se escribe RED y no se abre Reasoning.

## 1. Objetivo exacto

Determinar el residual mínimo para que un resultado long-horizon autorizado `A(N)` pueda ser encaminado una sola vez hacia el owner canónico de Execution ya existente, produzca `E(N)` y registre esa adquisición mediante el Episode owner, preservando P2/A2/E2 histórico y terminando antes de Reasoning re-entry.

Corte buscado:

`long-horizon A(N) + eligible_for_existing_execution`
→ existing `GovernedMultiStepInvestigationExecutionReentryV1.consume(...)` exactamente una vez
→ exact `GovernedInvestigationExecutionReentryResult` / evidence envelope / resulting episode state
→ elegibilidad declarativa para Reasoning cuando corresponda
→ **STOP antes de Reasoning**.

## 2. Owner canónico de Execution ya está N-step

La autoridad productiva correcta continúa siendo:

- `app/governed_multistep_investigation_execution_reentry.py`
- `GovernedMultiStepInvestigationExecutionReentryV1`

Ese owner ya fue generalizado y certificado para step N. Los contratos existentes cubren explícitamente:

- A3 → E3 con una sola invocación de Execution y un solo record de adquisición;
- E3 con budget restante y `eligible_for_reasoning_reentry=True`;
- A4 → E4 con budget agotado;
- compatibilidad histórica A2 → E2;
- STOP antes de Reasoning.

Por tanto, **no existe un gap en Execution canónica** y no corresponde modificarla, duplicarla ni envolverla con otro executor.

## 3. Bridge long-horizon existente y residual real

El wiring histórico está en:

`app/governed_long_horizon_investigation_e2_execution_reentry.py`

Owner de wiring:

`GovernedLongHorizonInvestigationE2ExecutionReentryV1`

Resultado histórico:

`GovernedInvestigationE2ExecutionAdmissionResult`

Ese bridge ya delega correctamente una sola vez al owner canónico y conserva thread/checkpoint/originating-reasoning lineage. El residual está limitado a supuestos A2/E2 terminales todavía hard-coded.

### 3.1 Guards pre-Execution todavía rígidos

`_eligible(...)` exige actualmente:

- `authorization_reentry.current_step == 2`;
- `authorization_reentry.remaining_acquisitions == 1`;
- `state.current_step == 2`;
- `state.remaining_acquisitions == 1`.

Estos guards impiden que un A3 o A4 long-horizon elegible llegue al owner N-step ya certificado.

### 3.2 Validación post-Execution todavía rígida

`_valid_acquired_e2(...)` exige actualmente:

- `execution_reentry.current_step == 2`;
- `execution_reentry.remaining_acquisitions == 0`;
- `state.current_step == 2`;
- `state.remaining_acquisitions == 0`.

Esto sólo describe el caso histórico E2 terminal de budget 2. Para budget 4, E3 correctamente registrado debe quedar en step 3 con remaining 1 y `AWAITING_REENTRY`.

### 3.3 Resultado long-horizon todavía fuerza agotamiento de budget para Reasoning

`GovernedInvestigationE2ExecutionAdmissionResult.__post_init__` deriva `eligible_for_existing_reasoning_reentry` exigiendo además:

`resulting_episode_state.remaining_acquisitions == 0`.

Ese supuesto es incompatible con el owner canónico actual: una adquisición E3 válida puede y debe volver a Reasoning aun cuando quede una adquisición disponible. La elegibilidad para Reasoning deriva de una adquisición `ACQUIRED` correctamente registrada y de `AWAITING_REENTRY`, no del agotamiento del budget.

## 4. Invariante correcto A(N) antes de Execution

El bridge long-horizon puede delegar únicamente cuando conserva simultáneamente:

1. admission long-horizon en estado `AUTHORIZED`;
2. decisión exacta `MAY_INITIATE`;
3. `eligible_for_existing_execution=True`;
4. una sola invocación previa de Authorization;
5. `authorization_reentry` y `authorization_product` canónicos presentes;
6. `2 <= current_step <= state.max_acquisitions`;
7. `state.consumed_acquisitions == current_step - 1`;
8. `remaining_acquisitions > 0` antes de ejecutar;
9. `authorization_reentry.current_step == state.current_step`;
10. `authorization_reentry.remaining_acquisitions == state.remaining_acquisitions`;
11. exact episode / requirement / plan / authorization / source / snapshot lineage;
12. exact planning product, requirement y authorization product preservados.

El bridge no decide Authorization ni presupuesto. Sólo valida y reenvía el exacto A(N) al owner existente.

## 5. Invariante correcto E(N) después de Execution

Para un resultado canónico `ACQUIRED`:

1. `execution_reentry.authorization_reentry` debe ser exactamente el A(N) recibido;
2. Execution se invoca exactamente una vez;
3. Episode record se invoca exactamente una vez;
4. evidence envelope se preserva por identidad;
5. execution id debe ser nuevo respecto al Episode previo;
6. requirement / plan / authorization / source / snapshot lineage debe permanecer exacto;
7. `execution_reentry.current_step == authorization_reentry.current_step`;
8. resulting state `current_step` conserva ese mismo step;
9. resulting state debe quedar `AWAITING_REENTRY`;
10. `remaining_acquisitions` posterior debe coincidir con el valor producido por el Episode owner, no con cero hard-coded;
11. `eligible_for_existing_reasoning_reentry` puede ser verdadero para toda adquisición `ACQUIRED` correctamente registrada cuando el owner canónico ya expone `eligible_for_reasoning_reentry=True`.

Ejemplos constitucionales:

- histórico budget 2: A2 rem1 → E2 rem0;
- budget 4: A3 rem2 → E3 rem1;
- budget 4: A4 rem1 → E4 rem0.

## 6. Compatibilidad histórica obligatoria

La generalización posterior debe preservar:

- clase pública histórica `GovernedLongHorizonInvestigationE2ExecutionReentryV1`;
- resultado público `GovernedInvestigationE2ExecutionAdmissionResult`;
- status enum histórico;
- P2/A2/E2 budget-2 exactamente soportado;
- una única llamada al owner canónico;
- un único record de adquisición;
- ausencia de retry;
- ausencia de Reasoning invocation;
- ausencia de Planning/Authorization re-invocation;
- ausencia de nuevos executor/gateway/manager/loop.

Los nombres históricos con `E2` pueden mantenerse por compatibilidad pública; no justifican conservar semántica step-2 interna.

## 7. Documento histórico que queda superado en un punto

La reconciliación anterior `ROBY_XI_2_CAP_11_AUTHORIZATION_STEP_N_TO_EXISTING_EXECUTION_REENTRY_SURGICAL_RECONCILIATION.md` indicaba que el bridge long-horizon E2 no debía generalizarse dentro de aquel bloque. Esa decisión era correcta para el alcance de **generalizar primero el owner canónico**.

Ese owner ya está generalizado y certificado. El frontier actual es específicamente el wiring long-horizon A(N) → E(N). Por tanto, ahora sí corresponde generalizar **el mismo bridge histórico existente**, sin crear una segunda capa de wiring.

## 8. Superficie mínima del futuro GREEN

Si el RED confirma este diagnóstico, la modificación productiva debe limitarse a:

`app/governed_long_horizon_investigation_e2_execution_reentry.py`

No debe tocarse:

- `app/governed_multistep_investigation_execution_reentry.py`;
- `app/governed_level2_read_only_execution_gateway.py`;
- `app/governed_multistep_investigation_episode.py`;
- Authorization canónica;
- Reasoning re-entry;
- `.roby/config.json`.

## 9. RED contractual recomendado

El próximo RED debe congelar al menos:

- long-horizon A3 elegible → existing Execution owner exactamente una vez → E3;
- E3 registra adquisición exactamente una vez;
- E3 conserva step 3 y queda con remaining 1 bajo budget 4;
- E3 expone elegibilidad para existing Reasoning sin invocarlo;
- long-horizon A4 elegible → E4 con remaining 0;
- exact R(N)/P(N)/A(N)/E(N)/source/snapshot/episode lineage;
- execution id nuevo respecto al Episode previo;
- histórico A2→E2 permanece soportado;
- no se invoca Reasoning, Planning ni Authorization;
- no se crea executor/gateway/manager/loop nuevo;
- el owner canónico de Execution permanece sin cambios.

Los fallos RED esperados deben localizarse en el bridge long-horizon antes o después de la llamada canónica por los guards E2 hard-coded, nunca en el owner N-step de Execution.

## 10. Dictamen final

**No falta Execution N-step. Falta generalizar el wiring long-horizon histórico A2→E2 para transportar A(N) hacia el owner N-step ya certificado y preservar E(N).**

Frontera al terminar el futuro GREEN:

`A(N) → existing Execution re-entry E(N) → eligible_for_existing_reasoning_reentry`

con **STOP absoluto antes de Reasoning**.
