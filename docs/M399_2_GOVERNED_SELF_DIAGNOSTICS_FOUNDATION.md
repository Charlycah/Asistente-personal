# M399.2 — Governed Self-Diagnostics Foundation

## Propósito

M399.2 abre el cuerpo principal de **Governed Self-Diagnostics & Self-Maintenance**
con una frontera deliberadamente pequeña y verificable:

**Observación → tendencia → anomalía**

Este incremento no avanza todavía a hipótesis, confianza causal, propuesta,
sandbox, patch, diff ni decisión de mantenimiento. **predicción ≠ certeza** y una
anomalía observada no demuestra su causa.

## Autoridad y reutilización

`GovernedSelfDiagnostics` expone la autoridad técnica única `self_diagnostics`
para normalizar series de evidencia operacional explícita. No reemplaza las
autoridades que producen la evidencia: runtime readiness, provider health,
conversational observability, M391 integral evidence y otras vistas certificadas
conservan sus competencias y estado.

Tampoco sustituye `UnifiedBrain.diagnostics` ni el nodo cognitivo
`unified_diagnostics` de M387.9. Ese contrato continúa describiendo el cierre y
la cobertura del ciclo cognitivo; M399.2 sólo trabaja con métricas técnicas
explícitas suministradas por su autoridad fuente.

## Observaciones

Toda `DiagnosticObservation` exige:

- `observation_id` explícito y único dentro del diagnóstico;
- `source_authority` explícita;
- métrica explícita;
- valor numérico ya observado;
- timestamp timezone-aware;
- códigos de evidencia opcionales, nunca inventados.

La autoridad no mezcla fuentes ni métricas diferentes dentro de una serie. No
consulta por sí sola red, hardware, archivos, procesos, memoria o providers.

## Tendencia

La tendencia se calcula únicamente sobre los valores suministrados y conserva
los `observation_id` utilizados. Una sola muestra produce
`insufficient_evidence`; dos o más muestras pueden resultar `stable`,
`increasing` o `decreasing`. La tendencia describe cambio observable y no causa.

## Anomalía

Una anomalía sólo puede surgir frente a un `DiagnosticThreshold` explícito. El
umbral declara métrica, límite, dirección y cantidad mínima de violaciones
consecutivas. M399.2 conserva las observaciones que reproducen el hallazgo.

Una anomalía **no formula hipótesis**, no asigna causa, no prescribe solución y
no eleva autoridad. El rationale fija expresamente `no_cause_inferred` y
`no_corrective_action_performed`.

## Límites permanentes de M399.2

- sólo lectura;
- sin persistencia nueva;
- sin background monitoring ni polling;
- sin reparación ni rollback;
- sin generación de patch o diff;
- sin `.roby/review/proposals/...` todavía;
- sin sandbox;
- sin modificar código operativo;
- sin convertir anomalía en certeza causal;
- sin cambiar las autoridades fuente.

Los pasos posteriores de M399 podrán añadir hipótesis y confianza sólo después
de conservar esta evidencia reproducible y deberán mantener la decisión humana
antes de cualquier cambio operativo.
