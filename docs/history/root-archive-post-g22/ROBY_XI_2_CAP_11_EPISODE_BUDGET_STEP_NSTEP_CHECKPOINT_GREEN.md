# ROBY XI.2 — CAP-11 Governed Horizon Generalization
## GREEN quirúrgico: Episode budget/step N-step + exact checkpoint continuity

Baseline de entrada certificada: **13.669 PASS + Ruff limpio**.

## Alcance cerrado

Este GREEN generaliza únicamente la constitución del owner existente de episodio y el carrier pasivo de continuidad. No hace productivos P3/A3/E3/RR3 y no crea una segunda autoridad de Planning, Authorization, Execution, Reasoning, budget o stopping.

Owners preservados:

- Episode/budget/stopping: `GovernedMultiStepInvestigationEpisodeBoundaryV1`.
- Continuidad pasiva: `GovernedLongHorizonInvestigationContinuityV1`.

## Constitución gobernada resultante

Se declara una única cota constitucional:

`GOVERNED_INVESTIGATION_MAX_ACQUISITIONS = 4`

El presupuesto histórico por defecto sigue siendo `2`. El owner acepta únicamente enteros en `1..4`; `bool`, cero, negativos y valores mayores que cuatro fallan cerrado.

`start(..., max_acquisitions=2)` y la llamada histórica sin argumento conservan exactamente el fingerprint/episode ID previo. Los budgets distintos de 2 entran en el fingerprint para evitar colisiones entre episodios con igual lineage y distinta constitución.

El estado admite ahora `1 <= current_step <= max_acquisitions <= 4`, exige que el lineage de requirements corresponda al step actual y mantiene los invariantes existentes de acquisitions/plans/authorizations/executions/reentries.

## Transiciones N-step

`record_reentry(...)` deja de cerrar por ser RR2: cierra únicamente cuando `consumed_acquisitions == max_acquisitions`. Si queda budget, retorna `CONTINUE_ALLOWED + AWAITING_REQUIREMENT`.

`evaluate_continuation(...)` cierra sólo si no queda budget; una requirement nueva y válida incrementa exactamente `current_step + 1`, la añade al lineage y deja el episodio en `READY_FOR_PLANNING`. No invoca Planning.

Para preservar compatibilidad observable del ciclo histórico budget-2, sus rationale codes históricos permanecen intactos en ese caso; los episodios generalizados usan rationale genérico.

## Checkpoint continuity

`GovernedPassiveInvestigationCheckpoint` transporta ahora `current_step` explícito junto con `max_acquisitions`, consumo, lineages, status, stopping y source/snapshot. El `current_step` participa en el fingerprint del checkpoint.

La validación del checkpoint reutiliza la misma cota constitucional del Episode owner; no existe un segundo hard-cap en continuidad.

`resume(...)` continúa siendo pasivo. Un checkpoint step 3 con budget restante puede producir `RESUME_CANDIDATE`; un checkpoint agotado sigue produciendo `BUDGET_REVIEW_REQUIRED`. Resume no modifica ni amplía el budget.

## Compatibilidad y límites

El ciclo productivo certificado de dos adquisiciones permanece sin cambios: default 2, ID histórico, RR2 terminal por budget agotado y consumidores P2/A2/E2/RR2 especializados.

Este GREEN no autoriza step 3 productivo. Siguen cerrados P3/A3/E3/RR3, cualquier scheduler/loop, nueva autoridad, persistencia, Memory/World Model write, background y retry.

## Validación focal

El contrato RED pasa completamente tras el GREEN y se añade una superficie GREEN específica para budget `1..4`, identidad histórica, checkpoint step 3, resume pasivo y ausencia de autoridad productiva step 3.
