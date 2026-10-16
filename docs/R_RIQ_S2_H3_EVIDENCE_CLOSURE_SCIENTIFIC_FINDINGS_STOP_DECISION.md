# ROBY XI.2 — R-RIQ-S2-H3-EVIDENCE-CLOSURE
## Scientific Findings Consolidation & STOP Decision (Documentary)

**Estado:** ACTA DOCUMENTAL CANDIDATA — verificación local y aprobación formal del Owner pendientes.  
**Gobierno:** `STOP_PRODUCTIVE: ACTIVE`; `H3_EXPERIMENTS: NOT_AUTHORIZED`.  
**Naturaleza:** consolidación de evidencia ya inspeccionada; no nueva auditoría, prueba, ejecución, modificación de código ni cambio de autoridad.

## 1. Propósito y precedencia

Consolidar los resultados de los tres documentos H3, declarar el límite científico de evidencia y cerrar la rama de trazado estático para evitar inspecciones redundantes:

1. `R_RIQ_S2_H3_EXPERIMENTAL_DESIGN_CANDIDATE_RATIONAL_ACTION_OUTCOME_BASELINES.md` — pregunta falsable, estratos, comparadores independientes, métricas y condiciones de admisión.
2. `R_RIQ_S2_H3_FEASIBILITY_CANONICAL_DECISION_OUTCOME_EVIDENCE_MAPPING.md` — contratos existentes y matriz de factibilidad.
3. `R_RIQ_S2_H3_CANONICAL_LINEAGE_TRACE_DECISION_JOURNAL_OUTCOME_SUPERVISION.md` — consumidores y ruta funcional específica confirmada estáticamente.

Conservar la reconciliación POST-H2: H2 continúa en `INSUFFICIENT_EVIDENCE` / STOP, sin inferir permisos de investigación H3. H1 y H4 permanecen como hipótesis del programa científico, no descartadas.

## 2. Pregunta científica y alcance de lo demostrado

**H3:** ¿ROBY selecciona acciones racionales, cumple restricciones gobernadas y obtiene resultados verificables comparables o superiores a baselines independientes? El protocolo documental define cómo falsar y medir la hipótesis, pero **no se ha ejecutado**.

**Evidencia estática concreta:**

- `core/controlled_autonomy/contracts.py`: `AutonomyDecision`, `DecisionOutcome` y `DecisionJournalEntry` expresan identidad y vínculo contractual de decisión/outcome.
- `core/controlled_autonomy/orchestrator.py`: genera una decisión y agrega inicialmente una entrada de diario sin outcome.
- `core/controlled_autonomy/first_capability.py`: la ruta `run()` exige `AUTHORIZE`, ejecuta una capacidad registrada, solicita supervisión y devuelve `CapabilityRunResult` con outcome y supervision.
- `core/controlled_autonomy/outcome_supervisor.py`: `OutcomeSupervisionResult` exige correspondencia entre identidades de decisión/candidato y resultado.
- `core/controlled_autonomy/decision_journal.py` y `persistent_journal.py`: diarios en memoria y JSONL con outcome opcional; la capacidad del esquema no prueba actualización histórica posterior.
- `core/executive_runtime_integration/integration.py`: composición del diario con el runner; `explain_decision()` solo adjunta outcome desde `last_autonomy_result` cuando coincide.

**Inferencia permitida:** `SPECIFIC_DECISION_OUTCOME_SUPERVISION_PATH_CONFIRMED_STATICALLY`. No es una traza universal, ni evidencia de que una acción real se haya ejecutado durante este estudio.

## 3. Matriz consolidada de suficiencia

| Dimensión | Dictamen | Límite |
|---|---|---|
| Contratos de identidad decisión–outcome | `CONFIRMED_STATICALLY` | Dominio controlled_autonomy |
| Gate de autorización y runner registrado | `CONFIRMED_STATICALLY_IN_SPECIFIC_PATH` | No cobertura universal |
| Outcome y supervisión correlacionados | `CONFIRMED_STATICALLY_IN_SPECIFIC_PATH` | Resultado en `CapabilityRunResult` |
| Diario inicial de decisión | `CONFIRMED_STATICALLY` | Entrada inicial sin outcome |
| Persistencia histórica completa del outcome | `NOT_DEMONSTRATED` | No backfill demostrado |
| Recuperación histórica de supervisión | `NOT_DEMONSTRATED` | No traza histórica completa demostrada |
| Observación independiente del resultado real | `NOT_DEMONSTRATED` | Sin casos adjudicados |
| Acceso científico gobernado | `NOT_DEMONSTRATED` | Contrato o repositorio no equivale a permiso |
| Baselines independientes y corpus | `NOT_PREPARED` | Diseño, no evidencia |
| Comparación de eficacia o racionalidad | `NOT_DEMONSTRATED` | Sin experimento |

## 4. Dictamen científico y decisión de STOP

- `H3_FEASIBILITY: PARTIALLY_FEASIBLE`.
- `H3_SPECIFIC_CANONICAL_LINEAGE: CONFIRMED_STATICALLY`.
- `H3_COMPLETE_HISTORICAL_LINEAGE: NOT_DEMONSTRATED`.
- `H3_AUTHORIZED_RESEARCH_ACCESS: NOT_DEMONSTRATED`.
- `H3_INDEPENDENT_BASELINES: DESIGN_ONLY`.
- `H3_EXPERIMENTAL_ADMISSION: EXPERIMENT_NOT_ENABLED`.
- `H3_STATIC_LINEAGE_BRANCH: STOP — DOCUMENTARY_CLOSURE_PROPOSED`.

**Razón:** la revisión acotada encontró una conexión funcional específica; inspecciones estáticas adicionales de la misma ruta no resuelven por sí solas las carencias de acceso, persistencia verificable, resultados observados y adjudicación independiente. La falta de evidencia **no** es refutación de H3 ni defecto productivo demostrado. No extrapolar a inteligencia general o superioridad humana.

## 5. Reapertura excepcional — evidencia nueva y admisión

No reabrir por mera posibilidad. Exigir un paquete nuevo y verificable con:

1. Autoridad y ruta canónica identificadas, reconciliadas con documentación maestra, inventarios y capacidades existentes, sin crear autoridad paralela.
2. Autorización específica y gobernada de acceso a los registros concretos, con minimización y límites de privacidad; preservar la frontera Desktop `metadata-only` y controles M63/M158.
3. Casos reales elegibles con identidad correlacionada de decisión, disposición de autorización, estado de ejecución, outcome y supervisión, incluyendo ausencia/indeterminación explícita; procedencia verificable.
4. Ground truth y baseline independientes, corpus, denominadores, estratos, adjudicación y protocolo pre-registrados; distinguir propuestas no ejecutadas de éxitos observados.
5. Revisión de seguridad, límites de acción y aprobación expresa del Owner para el experimento exacto. Cualquier modificación productiva requiere su propio circuito gobernado RED/GREEN y certificación.

Si falla cualquiera de estas condiciones: `EXPERIMENT_NOT_ENABLED` y mantener STOP. No instalar observadores, diarios, ejecutores o supervisores duplicados como respuesta automática.

## 6. Retorno al plan científico maestro

Tras incorporación, cotejo de SHA-256 y aprobación formal, elevar este cierre al plan maestro R-RIQ-S2 y elegir el siguiente trabajo científico por **nueva evidencia, valor y factibilidad**, sin declarar H1/H4 aprobadas ni iniciar ensayos. El paso recomendado es una **reconciliación científica de cartera POST-H3**, exclusivamente documental, para decidir prioridad y no repetir H2/H3. No implica actualizar por sí mismo los documentos maestros.

## 7. Registro de gobierno y no acciones

`DOCUMENT: PREPARED_CANDIDATE`  
`LOCAL_SHA_VERIFICATION: PENDING`  
`OWNER_APPROVAL: PENDING`  
`H3_EXPERIMENTS: NOT_AUTHORIZED`  
`TESTS_EXECUTED: NONE`  
`PRODUCTIVE_CHANGES: NONE`  
`STOP_PRODUCTIVE: ACTIVE`

Este documento consolida los hallazgos previos, no certifica experimentalmente H3. La coincidencia de hash acredita integridad del archivo, no aprobación científica ni autorización de ejecución.
