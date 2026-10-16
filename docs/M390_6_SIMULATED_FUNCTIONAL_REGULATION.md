# M390.6 — Regulación Funcional Simulada

## Objetivo

Añadir regulación proporcional y determinista sobre el mundo interior simulado sin crear una segunda autoridad emocional, memoria afectiva ni autonomía nueva.

## Arquitectura

`SimulatedFunctionalRegulation` es un evaluador puro y subordinado. Recibe un `SimulatedInnerStateSnapshot` actual y, opcionalmente, un `ExplicitInnerContinuityReport` ya calculado por M390.3. Produce un `SimulatedFunctionalRegulationReport` inmutable; nunca construye o modifica snapshots.

`SimulatedInnerStateAuthority` conserva la única autoridad para construir el estado interior simulado. M377 conserva la única autoridad de modulación expresiva.

## Reglas funcionales

- Un estado estable y sin riesgo pasa sin regulación adicional.
- Riesgo explícito, alta preocupación, inestabilidad, conflicto o degradación de continuidad exigen cautela proporcional.
- Un cambio explícito amplio entre snapshots puede solicitar estabilización expresiva.
- Una única fuente relacional no puede, por sí sola, escalar la expresión afectiva.
- La única limitación expresiva que M390.6 puede proponer es `careful`; nunca puede forzar calidez, dirección o reparación.
- Ausencia de snapshot actual no se completa mediante inferencia.
- Un snapshot degradado no se reescribe ni se presenta como regulado con éxito.

## Límites

M390.6 no persiste, no usa reloj, no aprende, no crea memoria, no modifica personalidad, no crea objetivos, no ejecuta acciones, no toca runtime y no accede a `.roby/credentials.json`.
