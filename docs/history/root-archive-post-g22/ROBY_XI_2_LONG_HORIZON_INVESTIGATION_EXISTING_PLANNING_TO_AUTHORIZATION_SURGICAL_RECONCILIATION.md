# ROBY XI.2 — Long-horizon Investigation
## Reconciliación quirúrgica — Existing Evidence Acquisition Plan → Existing Governed Authorization

**Baseline oficial de entrada:** 13.568 PASS + Ruff limpio.

## Hallazgo

El residual no requiere un nuevo owner de Authorization. ROBY XI.2 ya posee la autoridad canónica `GovernedIndependenceAuthorizationBoundaryV1`, cuya decisión puede exponerse sin operacionalizarla mediante `GovernedIndependenceAuthorizationProductiveConsumptionV1`.

El producto certificado del bloque anterior, `GovernedInvestigationEvidencePlanningResult`, ya conserva el `planning_product` existente y deriva `eligible_for_authorization=True` exclusivamente de `PLANNED + PLANNABLE`.

## Corte productivo exacto

Entrada elegible:

`GovernedInvestigationEvidencePlanningResult`

con:

- status `PLANNED`;
- planning status `PLANNABLE`;
- `eligible_for_authorization=True`;
- planning product presente;
- lineage requirement/plan/source/snapshot consistente;
- producto no ejecutivo.

Delegación única:

`GovernedIndependenceAuthorizationBoundaryV1.evaluate(planning_product)`

Exposición gobernada:

`GovernedIndependenceAuthorizationProductiveConsumptionV1.consume(report)`

## Owner

La autoridad permanece:

`governed_independence_authorization_boundary`

El adapter long-horizon no decide por sí mismo, no recalcula políticas y no se convierte en autoridad.

## Prohibición de atajo histórico

No reutilizar `GovernedMultiStepInvestigationAuthorizationReentryV1`: ese reentry conserva invariantes específicos de continuación multi-step (`current_step == 2`, budget restante y lineage propio de esa ruta) que no pertenecen al resume admission bridge actual.

## Semántica del resultado

Una invocación exitosa de la autoridad puede producir `MAY_INITIATE`, `MUST_ASK`, `MUST_ABSTAIN` o `REVIEW_REQUIRED`. El bridge sólo preserva la decisión.

`eligible_for_existing_execution=True` puede derivar únicamente de `MAY_INITIATE`.

Esto NO equivale a ejecución autorizada dentro del bridge: `execution_authorized` permanece `False` y no se invoca ningún execution gateway.

## Corte de salida

El bloque termina en:

`Existing Evidence Acquisition Plan → Existing Governed Authorization → next-gate eligibility as derived data`

Residual posterior:

`Existing Governed Authorization → Existing Governed Execution Gateway`.
