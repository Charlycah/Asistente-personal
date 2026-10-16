# CAP-11 — Authorization step N → existing Execution re-entry — CONTRACT RED

Estado: RED contractual deliberado.

## Autoridad congelada

No se crea un nuevo executor. El único owner sigue siendo
`GovernedMultiStepInvestigationExecutionReentryV1`, reutilizando el gateway read-only
existente y `GovernedMultiStepInvestigationEpisodeBoundaryV1.record_acquisition(...)`.

## Contrato N-step

Una Authorization canónica de step N es ejecutable cuando mantiene autorización válida,
lineage exacto, step dentro del budget gobernado y budget restante positivo antes de la
adquisición.

Un ACQUIRED válido debe quedar en `AWAITING_REENTRY` y ser elegible declarativamente
para el Reasoning re-entry existente aunque todavía quede budget para adquisiciones
posteriores. Esa elegibilidad no autoriza ni invoca Reasoning.

## Compatibilidad

A2/E2 con budget 2 debe continuar funcionando exactamente.

## STOP line

El corte termina después de Execution + `record_acquisition`. No se invoca Reasoning,
no se crea R3/R4, no se replantea, no se reintenta y no se añade executor/loop/manager.

## Fallos deliberados esperados

La producción reconciliada conserva todavía semántica E2 terminal:
- `current_step == 2`;
- `remaining_acquisitions == 1` antes de ejecutar;
- `remaining_acquisitions == 0` después de ACQUIRED;
- Reasoning eligibility sólo con budget agotado.

Los tests N-step deben fallar exclusivamente contra esos supuestos.
