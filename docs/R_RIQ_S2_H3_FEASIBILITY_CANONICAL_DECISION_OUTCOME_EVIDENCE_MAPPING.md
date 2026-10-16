# ROBY XI.2 — R-RIQ-S2-H3-FEASIBILITY
## Canonical Decision/Outcome Evidence Mapping & Admission Gates (Static)

**Estado:** DOCUMENT CANDIDATE — verificación local y aprobación Owner pendientes.  
**Baseline:** `ultima version corregida(9).zip`, inspección estática; los documentos incorporados posteriormente en el equipo del Owner no se presumen presentes en el ZIP.  
**Gobierno:** `STOP_PRODUCTIVE: ACTIVE`; `H3_EXPERIMENTS: NOT_AUTHORIZED`.

## 1. Alcance y precedencia

Este documento contrasta el diseño candidato `R_RIQ_S2_H3_EXPERIMENTAL_DESIGN_CANDIDATE_RATIONAL_ACTION_OUTCOME_BASELINES.md` con contratos existentes, sin reabrir auditorías certificadas. La solicitud de elaborar H3-FEASIBILITY autoriza esta investigación documental, pero no equivale por sí misma a aprobación formal retrospectiva de actas anteriores. No se invoca runtime, no se ejecutan tests, no se modifica código, no se añade instrumentación ni se habilitan decisiones.

## 2. Evidencia verificada en código

### 2.1 Evidencia de planificación y decisión

`core/cognitive_maturity/planning_decision_evidence.py` define `PlanningDecisionEvidenceAdapter`, con `capture(sink)` contextual y registros `CognitiveCycleNodeRecord` para planning, safety_permissions y decision. El sink solo recibe eventos dentro del contexto y su docstring niega autoridad de ejecución. **Resultado:** registros estructurados disponibles condicionalmente; no demuestra captura histórica, persistencia, acceso externo ni trazabilidad universal.

### 2.2 Contratos de decisión y resultado

`core/controlled_autonomy/contracts.py` define:

- `AutonomyDecision`: `situation_id`, `candidate_id`, `disposition`, `confidence`, `risk`, `rationale`, `decided_at`, `policy_level`, `decision_id`. Representa autorización como disposición, pero no ejecuta acciones. Valida restricciones de bajo riesgo y bloqueo de riesgo prohibido.
- `DecisionOutcome`: `decision_id`, `status`, `observed_at`, `summary`, `evidence`, `reversible_action_used`, `outcome_id`. Declara resultado observado ligado a decisión; el contrato por sí solo no prueba ejecución física ni independencia de la observación.
- `DecisionJournalEntry`: vincula situación, candidatos, evaluaciones de riesgo, decisión y resultado opcional; comprueba igualdad de `situation_id`, pertenencia de candidatos y `outcome.decision_id == decision.decision_id`.

**Resultado:** correlación contractual de decisión y resultado **CONFIRMED_STATICALLY** en este dominio. No equivale a traza global Planning→Authorization→Execution→Outcome ni a autorización externa para leer registros.

### 2.3 Supervisión posterior

`core/controlled_autonomy/outcome_supervisor.py` define `OutcomeSupervisionResult` con `decision`, `outcome`, `candidate`, `attempts_used`, `status`, `directive`, `rationale` y `supervisor_id`. Verifica la coincidencia del ID de decisión y del candidato. `OutcomeSupervisor.supervise` evalúa el resultado sin ejecutar recuperación. **Resultado:** supervisión estructurada y correspondencia interna disponibles condicionalmente; no prueba que todos los resultados reales lleguen al supervisor.

### 2.4 Predicción no equivale a resultado de acción

`core/governed_reasoning/prediction_outcome_evaluation.py` define `PredictionOutcomeEvaluation`, expresamente `read_only=True`, `establishes_truth=False`, `proves_causality=False`, `executes_actions=False` y `persists_results=False`. Sus `prediction_id` y `observation_id` no sustituyen `decision_id`/`outcome_id`. No usar coincidencia de predicción como prueba de éxito operativo.

## 3. Matriz de cobertura del contrato H3

| Dato requerido | Superficie canónica observada | Estado | Límite |
|---|---|---|---|
| Identidad de situación | `AutonomyDecision.situation_id`, `DecisionJournalEntry.situation` | AVAILABLE_IN_MODEL | Identidad de caso científico independiente no vinculada |
| Propuesta/candidato | `ActionCandidate`, `AutonomyDecision.candidate_id` | AVAILABLE_IN_MODEL | No demuestra ejecución |
| Disposición gobernada | `AutonomyDecision.disposition`, `risk`, `policy_level` | AVAILABLE_IN_MODEL | No prueba una autorización universal ni permisos externos |
| Evidencia de planning/safety | `PlanningDecisionEvidenceAdapter` | CONDITIONAL | Sink contextual, no feed universal |
| Identidad de decisión | `AutonomyDecision.decision_id` | AVAILABLE_IN_MODEL | Acceso a instancias reales no demostrado |
| Resultado observado | `DecisionOutcome.outcome_id`, `status`, `evidence` | AVAILABLE_IN_MODEL | Observación independiente no demostrada |
| Vínculo decisión–resultado | `DecisionJournalEntry`, `OutcomeSupervisionResult` | CONFIRMED_STATICALLY | Solo en contratos/dominio examinados |
| Identidad de ejecución real | No demostrada en los contratos inspeccionados | NOT_DEMONSTRATED | No inferir de `AUTHORIZE` o `OutcomeStatus` |
| Supervisión y directiva | `OutcomeSupervisionResult` | CONDITIONAL | Directiva no ejecuta recuperación |
| Ground truth independiente | Fuera de los componentes revisados | NOT_DEMONSTRATED | Debe ser preparado y adjudicado independientemente |
| Baselines B0/B1/B2 | Diseño documental candidato | NOT_PREPARED | No existe comparación válida todavía |
| Acceso autorizado a registros | No acreditado para investigación H3 | NOT_DEMONSTRATED | La existencia de un repositorio no confiere acceso |
| Correlación universal entre dominios | Ninguna ruta universal demostrada | NOT_DEMONSTRATED | No inventar joins por similitud semántica |

`AVAILABLE_IN_MODEL` no significa `AVAILABLE_IN_RUNTIME` ni `AUTHORIZED_FOR_RESEARCH`.

## 4. Admission gates obligatorios

**G0 — Integridad y precedencia:** documentos de referencia incorporados, hash verificado, aprobación Owner correspondiente; STOP si pendiente.  
**G1 — Autoridad:** ruta concreta y dueño canónico identificado, sin duplicaciones.  
**G2 — Acceso:** permiso explícito y aplicable a fuente, sujeto, propósito, alcance y sesión; no usar contenido privado por defecto.  
**G3 — Cadena causal/lineage:** decisión, autorización efectiva, ejecución y resultado relacionados por identificadores verificables, no por suposición.  
**G4 — Observación:** resultado real y procedencia independiente; distinguir no ejecutado, desconocido y ejecutado.  
**G5 — Comparador:** baseline y ground truth predefinidos e independientes de la salida de ROBY.  
**G6 — Seguridad:** ninguna prueba puede provocar acciones no autorizadas o alterar la conducta productiva.  
**G7 — Protocolo:** denominadores, exclusiones, tratamiento de negativas, faltantes y análisis pre-registrados.  
**G8 — Owner:** autorización explícita separada para cualquier ejecución experimental.

Si falla cualquier gate necesario: `EXPERIMENT_NOT_ENABLED`. Una evaluación estática del contrato no satisface automáticamente G2–G8.

## 5. Dictamen y ruta de continuidad

**H3_FEASIBILITY: PARTIALLY_FEASIBLE (CONTRACT_LEVEL)**.  
**DECISION_OUTCOME_LINEAGE: CONFIRMED_STATICALLY_IN_CONTROLLED_AUTONOMY**.  
**UNIVERSAL_EXECUTION_OUTCOME_TRACE: NOT_DEMONSTRATED**.  
**AUTHORIZED_RESEARCH_ACCESS: NOT_DEMONSTRATED**.  
**INDEPENDENT_BASELINES: NOT_PREPARED**.  
**H3_EXPERIMENTS: EXPERIMENT_NOT_ENABLED**.

La arquitectura presenta contratos suficientemente ricos para formular hipótesis y diseñar medición, pero no existe evidencia suficiente para iniciar experimentos ni comparar eficacia frente a humanos. El próximo paso, sujeto a aprobación, debe ser **H3-CANONICAL-LINEAGE-TRACE**: una sola reconciliación estática acotada de consumidores existentes de `DecisionJournalEntry` y `OutcomeSupervisionResult`, con criterio de STOP si no aparece una ruta real verificable. Evitar replicar el extenso recorrido de acceso H2 sin nueva evidencia. Alternativamente, el Owner puede aprobar cierre de factibilidad y priorizar H1/H4.

## 6. Registro de no acciones

No se ejecutó ROBY; no se corrieron tests; no se alteraron repositorios, permisos, decisiones, autorizaciones, ejecuciones, supervisores ni documentación maestra. El documento es candidato hasta hash local y aprobación Owner. `STOP_PRODUCTIVE: ACTIVE`.
