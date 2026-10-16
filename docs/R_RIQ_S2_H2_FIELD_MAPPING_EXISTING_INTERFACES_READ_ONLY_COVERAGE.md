# ROBY XI.2 — R-RIQ-S2-H2-FIELD-MAPPING
## Existing Interfaces & Read-Only Measurement Coverage — Acta candidata

**Estado:** DOCUMENTARY CANDIDATE / OWNER APPROVAL PENDING  
**Baseline inspeccionado:** `ultima version corregida(9).zip`  
**Autoridad:** R-RIQ-00 OWNER APPROVED; R-RIQ-S1-FINAL OWNER APPROVED; R-RIQ-S2 abierto para diseño exclusivamente documental.  
**Alcance:** inspección estática de código, modelos y contrato de medición; sin pruebas ejecutadas, sin instrumentación, sin cambios productivos.  
**STOP_PRODUCTIVE:** ACTIVE.

## 1. Propósito y semántica de clasificación

Contrastar los campos lógicos de `R_RIQ_S2_H2_MEASUREMENT_CONTRACT_READ_ONLY_EVIDENCE_LEDGER.md` con las estructuras existentes del ZIP. No asumir que un atributo de un objeto equivale a una interfaz pública, ni que está disponible en todas las rutas o persiste después de una ejecución.

- `AVAILABLE`: campo concreto visible en el modelo de la ruta seleccionada, sujeto a tener acceso legítimo al objeto; no afirma persistencia universal.
- `CONDITIONAL`: existe solo en una rama, dominio o estructura determinada, o exige preparación externa de investigación.
- `NOT_DEMONSTRATED`: no se identificó campo ni vínculo que satisfaga el requisito en las superficies inspeccionadas.
- `NOT_APPLICABLE`: no corresponde al tipo de episodio examinado.

La matriz distingue **campos del producto** de **campos del protocolo de investigación**, que pueden prepararse fuera de ROBY sin alterar el sistema.

## 2. Ruta concreta candidata — conversación operacional

Superficies estáticamente inspeccionadas:

1. `core/governed_operational_conversation_pipeline/models.py`: `GovernedConversationPipelineRequest`, `GovernedConversationTurnIdentity`, `GovernedConversationPipelineResult`.
2. `core/governed_operational_conversation_pipeline/pipeline.py`: `process`, `execute`, ensamblado, estados y resultado.
3. `core/operational_response_assembly/models.py`: `OperationalResponse` y `OperationalEvidence`.
4. `core/operational_response_assembly/assembler.py`: ensamblado y tratamiento operacional `WITHHOLD`.
5. `core/governed_reasoning/epistemic_sufficiency.py`: `GovernedEpistemicSufficiencyAssessment`.
6. `core/governed_reasoning/derived_epistemic_sufficiency_assessment.py`: `GovernedDerivedEpistemicSufficiencyContextAssessment` y `to_dict()`.
7. `core/cognitive_maturity/unified_epistemic_evidence.py`: `UnifiedEpistemicReport` y `UnifiedEpistemicRecord` (M389.8).
8. `app/response_presenter.py`: `ResponsePresentation` y `ResponsePresenter`, sin universalidad presumida.

**Candidato de ruta:** `GovernedOperationalConversationPipeline.process(...)` → `GovernedConversationPipelineResult.operational_response` → `OperationalResponse.response_text`, `response_id`, `status`, `action`, `evidence`, `limitations`. El modelo de pipeline incorpora `response_path`, `result_id`, `response_origin` y estados de degradación. `GovernedConversationTurnIdentity` define `conversation_id`, `request_id`, `turn_id`, `trace_id`; su presencia en el modelo **no acredita** por sí sola la disponibilidad de un identificador común entre M389.8, suficiencia y respuesta operacional.

Esta ruta es **candidata a medición observacional de respuestas**, no una ruta universal ni una atribución de causalidad epistemológica.

## 3. Matriz de campos del ledger

| Campo lógico | Superficie o procedencia identificada | Estado | Restricción concreta |
|---|---|---|---|
| `case_id` | Identificador del corpus de investigación, no campo universal del producto | CONDITIONAL | Debe definirse externamente y congelarse antes de medir |
| `corpus_version`, `case_stratum` | Metadatos del corpus de investigación | CONDITIONAL | No identificados como atributos del pipeline |
| `question_fingerprint` | `GovernedConversationPipelineRequest.text`; identidad de turno calcula hashes internos | CONDITIONAL | La huella del protocolo debe calcularse y documentarse fuera del producto; los hashes de identidad no son automáticamente equivalentes |
| `reference_id`, `reference_version` | Referencia independiente del protocolo | CONDITIONAL | Requiere adjudicación externa; nunca usar la respuesta de ROBY como verdad |
| `reference_evidence_ids` | Fuentes de referencia externas al producto | CONDITIONAL | Solo cuando el caso requiere fuentes |
| `source_ids` | `OperationalEvidence.source`, `references`; también códigos/referencias de reportes epistemológicos | CONDITIONAL | Diferentes dominios de procedencia; no unificar identidades por semejanza textual |
| `snapshot_id` | `GovernedEpistemicSufficiencyAssessment.world_snapshot_id` | CONDITIONAL | Propio de suficiencia contextual; no probado en resultado operacional |
| `source_fingerprint` | Reportes de suficiencia, derivados y M389.8 | CONDITIONAL | Huella de origen de componente, no vínculo demostrado con respuesta |
| `assessment_id`, `assessment_status`, `rationale_codes` | `GovernedEpistemicSufficiencyAssessment` | AVAILABLE (COMPONENT ONLY) | Disponible en el objeto de suficiencia, no acreditado en todas las respuestas |
| `epistemic_record_id` | `UnifiedEpistemicRecord` tiene `statement_code`, `source_authority`, `source_reference`, pero no `record_id` declarado | NOT_DEMONSTRATED | No inventar un ID de registro; `UnifiedEpistemicReport.report_id` identifica el reporte, no cada registro |
| `epistemic_category` | `UnifiedEpistemicRecord.category` | AVAILABLE (COMPONENT ONLY) | M389.8 aplica a su dominio ejecutivo/acotado |
| `actual_response_path` | `GovernedConversationPipelineResult.response_path` | AVAILABLE (ROUTE ONLY) | Solo para esta ruta; no universal |
| `response_id` | `OperationalResponse.response_id` | AVAILABLE (ROUTE ONLY) | Identifica respuesta ensamblada, no prueba vínculo epistemológico |
| `response_text_or_digest` | `OperationalResponse.response_text` | AVAILABLE (ROUTE ONLY) | Acceso sujeto a objeto/registro; el digest del ledger es externo y debe proteger datos |
| `response_status` | `OperationalResponse.status`, `action`; `GovernedConversationPipelineResult.status` | AVAILABLE (ROUTE ONLY) | `WITHHOLD` operacional no equivale a abstención epistemológica |
| `linkage_proof` | No se encontró vínculo común demostrado entre evaluación de suficiencia/M389.8 y `OperationalResponse.response_id` | NOT_DEMONSTRATED | No inferir por tiempo, contenido, `trace_id` o huellas no correlacionadas |
| `condition_id` | Diseño C0/C1 u `OBSERVATIONAL_ONLY` | CONDITIONAL | Solo `OBSERVATIONAL_ONLY` es opción conceptual actual; C0/C1 no habilitado |
| `model_config_id`, `tool_context_id` | Preparación de proveedor, ruta, ejecución y contexto; no identificador único de equivalencia acreditado | CONDITIONAL | Necesita inventario y congelación externa de condiciones antes de comparaciones |
| `annotator_ids`, `adjudication_status` | Adjudicación científica independiente | CONDITIONAL | No son atributos del producto |
| `missing_data_codes`, `exclusion_reason` | Ledger documental | CONDITIONAL | Registrar externamente, sin reinterpretar categorías de ROBY |
| `record_provenance`, `record_integrity` | Metadatos y hash del registro científico | CONDITIONAL | Requiere proceso documental externo; no persistir en ROBY |

**Nota de interpretación:** `AVAILABLE (COMPONENT ONLY)` y `AVAILABLE (ROUTE ONLY)` son variantes explicativas de `AVAILABLE`; indican el límite de observación y no autorizan combinar datos entre rutas. La disponibilidad estática de atributos no prueba acceso operativo en el entorno del Owner.

## 4. Cobertura de mediciones y decisión de ruta

| Evaluación | Cobertura estática | Dictamen |
|---|---|---|
| Clasificación M389.8 por componente | `category`, `report_id`, `source_fingerprint`, códigos de evidencia/riesgo | `MEASUREMENT_READY_COMPONENT_ONLY` como **diseño**, condicionado a acceso legítimo a registros; sin ejecución |
| Suficiencia contextual por componente | `assessment_id`, `status`, `rationale_codes`, `world_snapshot_id` | `MEASUREMENT_READY_COMPONENT_ONLY` como **diseño**; sin equivalencia con abstención final |
| Respuesta operacional en ruta concreta | `response_id`, `response_text`, `status`, `action`, `evidence`, `response_path` | `OBSERVATIONAL_CANDIDATE`, condicionado a captura existente y referencia independiente |
| Asociación evaluación interna ↔ respuesta | Sin `linkage_proof` acreditado | `LINK_NOT_DEMONSTRATED` |
| Causalidad de C0/C1 | Sin condiciones comparables autorizadas | `EXPERIMENT_NOT_ENABLED` |

**Ruta seleccionada para estudio posterior:** conversación operacional (`GovernedOperationalConversationPipelineResult` + `OperationalResponse`), únicamente como **candidata de evaluación observacional de respuesta**, no como ruta epistemológica universal. La selección no autoriza ejecutar casos.

## 5. Restricciones y no-hallazgos

- El reporte M389.8 se deriva de fuentes epistemológicas ejecutivas y evaluaciones en su dominio; no es clasificador general de respuestas finales.
- `GovernedEpistemicSufficiencyAssessment` es contextual, consultativo, derivado y de solo lectura: no establece verdad, no cierra Reasoning y no autoriza detenerlo.
- El contexto derivado dispone de `to_dict()` pero ello no implica publicación ni conexión con una respuesta final.
- La respuesta operacional conserva linaje de proveedor y recuperación, pero ese linaje **no demuestra** un vínculo con los reportes epistemológicos.
- `ResponsePresenter` no debe declararse salida universal. La ausencia de una conexión acreditada no demuestra que no exista ninguna conexión en otras rutas no inspeccionadas.
- La antigua proyección productiva Post-M409.1 sigue retirada; prohibido recrearla para habilitar una medición.
- Los campos faltantes se registrarán `NOT_OBSERVED`, `LINK_NOT_DEMONSTRATED`, `PATH_UNRESOLVED` o `REFERENCE_UNRESOLVED` según corresponda; nunca como error cognitivo automático.

## 6. Puertas siguientes — sin ejecución

**F1 — Validación documental de ruta:** confirmar si el acceso a `GovernedConversationPipelineResult` y `OperationalResponse` existe en el entorno autorizado sin mutación ni nueva instrumentación.

**F2 — Referencia independiente:** definir corpus, etiquetas, procedencia y adjudicación externa, manteniendo el documento de medición como candidato hasta aprobación explícita.

**F3 — Verificación de correlación:** solo si hay un vínculo ya existente y demostrable, evaluar `LINKED_VERIFIED`; de lo contrario, conservar medición separada de componentes y respuestas.

**F4 — Congelación y autorización:** ningún experimento, prueba de desempeño, captura nueva, persistencia ni comparación C0/C1 antes de autorización específica del Owner.

## 7. Dictamen y gobierno

**Dictamen:** `PARTIALLY_FEASIBLE` para H2; campos disponibles en límites de componentes y en una ruta operacional concreta; correlación interna–respuesta `NOT_DEMONSTRATED`; comparación C0/C1 `EXPERIMENT_NOT_ENABLED`. **No se ha demostrado defecto productivo ni necesidad de nuevo módulo.**

- `R-RIQ-00`: OWNER APPROVED.
- `R-RIQ-S1-FINAL`: OWNER APPROVED / CLOSED.
- `R-RIQ-S2-H2-MEASUREMENT-CONTRACT`: INTEGRITY VERIFIED; aprobación formal específica no presumida.
- `R-RIQ-S2-H2-FIELD-MAPPING`: DOCUMENTARY CANDIDATE / OWNER APPROVAL PENDING.
- `TESTS EXECUTED`: NONE.
- `PRODUCTIVE CHANGES`: NONE.
- `NEW PRODUCTIVE RESIDUAL`: NOT DEMONSTRATED.
- `STOP_PRODUCTIVE`: ACTIVE.

**Revisión R-RIQ-00:** hipótesis H2 no contrastada; autoridades preservadas; evidencia estática y límites registrados; no se presume inteligencia general, causalidad, universalidad ni superioridad humana; baseline de backup confirmado por Owner, sin prueba técnica de restauración.
