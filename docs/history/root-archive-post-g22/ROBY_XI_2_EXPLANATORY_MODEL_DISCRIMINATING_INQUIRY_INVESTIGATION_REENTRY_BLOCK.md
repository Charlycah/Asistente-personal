# ROBY XI.2 — Explanatory Model → Discriminating Inquiry → Investigation Re-entry

**Baseline de entrada:** 13.508 PASS + Ruff limpio.

## Reconciliación

No se creó un nuevo motor de curiosidad, planificación, investigación ni generación
de hipótesis. La arquitectura ya poseía:

- `DiscriminatingEvidenceRequirement` bajo `governed_reasoning`;
- `GovernedLevel2BProductiveEntryFoundationV1` para admisión al lifecycle de
  investigación existente;
- Evidence Acquisition Planning, authorization, execution y reasoning re-entry
  históricos bajo sus autoridades existentes.

El residual era de composición productiva: el modelo explicativo ordinario podía
contener un requisito discriminante exacto, pero ese requisito no entraba desde el
runtime oficial al boundary de investigación.

## Implementación

Se añadió una superficie de composición:

`app/governed_explanatory_model_investigation_reentry.py`

`GovernedExplanatoryModelInvestigationReentryV1` consume únicamente un
`GovernedExplanatoryModelProductiveConsumption` ya certificado.

Si existe exactamente un `DiscriminatingEvidenceRequirement`, conserva su identidad,
`source_reference` y `world_snapshot_id`, y lo entrega sin reescritura al
`GovernedLevel2BProductiveEntryFoundationV1` existente.

La admisión usa como lineage de origen el `result_id` del episodio de razonamiento
productivo que produjo el modelo.

El gateway oficial almacena el resultado por el mismo `owner + session + turn` y
expone referencias de la re-entry sólo para ese turno.

## Fail closed

- cero requirements → `NO_DISCRIMINATING_INQUIRY`, sin episodio;
- más de un requirement → `AMBIGUOUS_INQUIRY`, sin selección arbitraria;
- rechazo del boundary existente → `REVIEW_REQUIRED`;
- sólo una admisión exacta y válida → `ADMITTED`.

No se inventa una pregunta ni se prioriza una alternativa fuera de una autoridad
existente.

## Frontera de ejecución

Este bloque **entra al lifecycle de investigación**, pero deliberadamente no ejecuta
el resto del lifecycle.

Una admisión válida deja el episodio abierto y elegible para la planificación
existente. No invoca planning, authorization, capabilities, execution ni evidence
acquisition. Tampoco inicia procesos de fondo.

Por tanto, no se salta ninguno de los gates Post-M409 ya certificados.

## Gobernanza preservada

- `governed_reasoning` conserva la autoridad del requisito;
- `multistep_investigation_episode_boundary` conserva la autoridad del episodio;
- no Memory;
- no World Model mutation;
- no Learning;
- no truth establishment;
- no automatic execution;
- no background process;
- no nueva autoridad.

El presupuesto histórico del episodio permanece en máximo 2 adquisiciones y comienza
con 0 consumidas.

## Validación focal

Se añadieron 6 tests end-to-end para:

1. modelo explicativo causal ordinario → requirement → episode admission;
2. identidad y lineage exactos;
3. referencias same-turn;
4. modelo sin requirement no inicia investigación;
5. ausencia de planning/authorization/execution/evidence acquisition;
6. preservación de autoridad y presupuesto bounded del episodio.

Perímetro ampliado afectado: **64 PASS**.

`py_compile` pasó para los archivos modificados y el test nuevo. El test histórico de
import-boundary también forma parte del perímetro verde.

La promoción oficial permanece sujeta a:

`ruff check .`

`pytest -q`

Resultado completo esperado si no existen cambios ajenos al bloque: **13.514 PASS**.
