# ROBY XI.2 — Evidence-driven Explanatory Model Revision
## GREEN — cierre gobernado V1 → evidencia → V2

**Baseline de entrada:** 13.521 PASS + Ruff limpio, certificada localmente por el usuario.

## Objetivo

Cerrar productivamente el feedback loop ya abierto por la cadena de investigación:

`Explanatory Model V1`
→ `DiscriminatingEvidenceRequirement`
→ investigación / adquisición gobernada
→ `GovernedLevel2ReasoningReentryResult`
→ reevaluación del mismo conjunto de hipótesis
→ discriminación revisada
→ `Explanatory Model V2`
→ Reasoning consultivo.

No se crea un nuevo motor cognitivo ni una nueva autoridad. La revisión es una composición bajo `governed_reasoning` y reutiliza `GovernedExplanatoryModelProductiveConsumptionV1`, la discriminación multi-hipótesis existente y `GovernedExplanatoryModelComposer`.

## Nuevo boundary de composición

`app/governed_explanatory_model_revision.py`

Contratos:

- `GovernedExplanatoryModelRevisionStatus`
- `GovernedExplanatoryModelRevision`
- `GovernedEvidenceDrivenExplanatoryModelRevisionV1`

Estados fail-closed:

- `REVISED`
- `REENTRY_REQUIRED`
- `LINEAGE_MISMATCH`
- `EVIDENCE_NOT_APPLIED`
- `HYPOTHESIS_SET_MISMATCH`
- `NO_MATERIAL_CHANGE`
- `REVIEW_REQUIRED`

## Condiciones para admitir V2

Una revisión válida exige simultáneamente:

1. re-entry gobernado exitoso y `evidence_id` explícito;
2. el `requirement_id` pertenece al V1 exacto;
3. `source_reference` y `world_snapshot_id` permanecen coherentes;
4. el conjunto de `hypothesis_id` de V1 se conserva exactamente;
5. la evidencia adquirida aparece realmente en la reevaluación;
6. la recomposición produce un `MODEL_CANDIDATE` válido;
7. V2 contiene un cambio material respecto de V1 en componentes, relaciones o requirements pendientes.

La evidencia nueva no puede convertirse automáticamente en verdad, falsedad o causalidad.

## Reachability productiva

`OfficialGovernedReasoningRuntimeGateway` añade:

- `bind_productive_explanatory_model_revision(...)`
- `productive_explanatory_model_revision(...)`
- `productive_explanatory_model_revision_reference_ids(...)`

El binding exige un `source_turn_id` exacto para recuperar V1. El resultado revisado queda ligado sólo al `(owner, session_id, turn_id)` de destino.

`CanonicalProductiveReasoningSource` añade:

- `explanatory_model_revision_context_lines(...)`

Y `reference_ids()` incorpora lineage de revisión sólo cuando el estado es `REVISED`.

`ReasoningRuntimeContributor` consume ese surface de manera estructural y exclusivamente consultiva.

## Lineage preservado

Una revisión productiva expone:

- `revision_id`
- `previous_model_id`
- `revised_model_id`
- `reentry_id`
- `requirement_id`
- `evidence_id`
- `source_reference`
- `world_snapshot_id`
- hipótesis materialmente modificadas
- requirements retirados / añadidos
- `source_fingerprint`

Esto permite demostrar V1 → evidencia → V2 sin mutar V1 ni reemplazar silenciosamente hipótesis.

## Fronteras de gobierno

La revisión permanece:

- read-only;
- consultiva;
- no persistente;
- no establece hechos;
- no establece verdad;
- no establece causalidad;
- no crea preguntas;
- no crea Learning;
- no modifica Memory;
- no modifica World Model;
- no ejecuta Structural Transfer;
- no registra reglas;
- no ejecuta acciones;
- no concede autoridad.

`GovernedLevel2ReasoningReentryFoundationV1` continúa siendo un adaptador genérico de una sola reevaluación y no absorbe autoridad de composición explicativa.

## Corrección de higiene heredada

El ZIP de entrada del asistente todavía contenía los dos imports no usados que el usuario ya había corregido localmente en el test CAP-19. La entrega GREEN incorpora esa misma corrección de higiene para que el ZIP vuelva a representar la baseline certificada.

No hay cambio semántico en CAP-19.

## Validación focal en entorno del asistente

Perímetro ejecutado:

- nuevo GREEN de revisión;
- Explanatory Model Composition;
- Discriminating Inquiry → Investigation Re-entry;
- ordinary multi-hypothesis reachability;
- CAP-19 cross-domain synthesis;
- auditoría global de ciclos del grafo productivo;
- contrato RED externo original.

Resultado: **40 PASS**.

Además, `py_compile` pasó sobre todos los archivos Python modificados y no hay líneas >88 en el perímetro modificado.

Ruff no está ejecutable en este entorno; por tanto la certificación oficial continúa dependiendo del gate local del usuario.

## Gate oficial de promoción

Ejecutar localmente:

`python scripts/generate_quality_baseline.py`

`ruff check .`

`pytest -q`

Si los 9 tests nuevos GREEN se agregan a la baseline certificada 13.521, el resultado esperado es **13.530 PASS + Ruff limpio**.
