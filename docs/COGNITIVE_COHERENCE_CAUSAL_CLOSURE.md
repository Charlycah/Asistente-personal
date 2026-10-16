# ROBY XI.2 — Cognitive Coherence & Causal Closure

## Estado del bloque

Este bloque consolida contratos ya implementados antes de abrir nuevas capabilities.

### Cross-Capability causal closure

La certificación se regenera contra la baseline actual y queda en:

- 8 PASS
- 2 PASS_BY_DESIGN
- 0 PARTIAL
- 0 FAIL

CCI-04 (`Memory -> Planning`) y CCI-10 (`Changed Conditions -> bounded replanning`)
ya poseen las pruebas causales que el harness exige. La discrepancia anterior provenía del
artefacto JSON congelado, que estaba atrasado respecto del código y de los tests existentes.

No se añade autoridad, manager, gateway, persistencia ni autonomía para cerrar esos escenarios.

### Commitment semantics reconciliation

WPS-06 deja de afirmar una causalidad productiva inexistente entre M199 y durable personal
commitments.

M199 continúa siendo Conversational Commitment Intelligence bounded al turno y owner/session.
RP.19 continúa siendo el lifecycle de cognitive commitment dentro de Cognitive Agenda.

`open_commitments` permanece como hook consumidor de compatibilidad sin source durable canónica
demostrada. No se crea `OpenCommitmentsManager` ni persistencia paralela.

### Regla

Primero reconciliar evidencia y contratos; sólo modificar producción cuando un gap causal real
permanezca después de esa reconciliación.
