# ROBY XI.2 — R-RIQ-S2-H2-MEASUREMENT-CONTRACT
## Read-Only Evidence Ledger & Evaluation Criteria — Documentary Candidate

**Estado:** DOCUMENTARY CANDIDATE / OWNER APPROVAL PENDING  
**Baseline de referencia:** `ultima version corregida(9).zip`  
**Marco:** R-RIQ-00 aprobado; R-RIQ-S1-FINAL aprobado; R-RIQ-S2 abierto para diseño documental  
**STOP_PRODUCTIVE:** ACTIVE  
**Ejecuciones nuevas:** ninguna. **Cambios de código:** ninguno.

## 1. Objetivo y frontera

Definir un contrato científico **documental** de registro de evidencia (ledger) y criterios de evaluación para H2 — calibración epistemológica. No es un contrato de software, interfaz nueva, autorización para instrumentar, ejecutar casos, alterar memoria, introducir un segundo Reasoning o reactivar la proyección retirada Post-M409.1.

La hipótesis H2 sigue **NO CONTRASTADA**. La factibilidad global previa es `PARTIALLY_FEASIBLE`; la comparación causal C0/C1 continúa `EXPERIMENT_NOT_ENABLED` con la evidencia disponible.

## 2. Autoridades y evidencia de partida

- `core/cognitive_maturity/unified_epistemic_evidence.py` (M389.8): categorías `observed`, `inferred`, `possible`, `insufficient_information` en su dominio acotado; no clasificador universal de respuesta final.
- `core/governed_reasoning/epistemic_sufficiency.py`: evaluación contextual con estados `sufficient`, `insufficient`, `indeterminate`, identificadores, referencias, razones y huella de fuentes; no concede detención ni establece verdad.
- `core/governed_reasoning/derived_epistemic_sufficiency_assessment.py`: contexto derivado, serializable y de solo lectura; no es evidencia ni afirmación nueva.
- `core/governed_operational_conversation_pipeline/pipeline.py` y `core/operational_response_assembly/assembler.py`: ruta operacional identificada; `WITHHOLD` operacional no equivale a abstención epistemológica.
- `app/response_presenter.py`: presentación en rutas identificadas; no está demostrada su universalidad.
- `tests/architecture/test_post_m409_1_epistemic_sufficiency_productive_projection_retirement.py`: prohíbe reintroducir `app/governed_epistemic_sufficiency_productive_consumption.py`.
- Actas R-RIQ-S2-H2-FEASIBILITY y R-RIQ-S2-H2-ROUTE-TRACE: observabilidad por componente, no correlación universal hasta respuesta final.

## 3. Unidad, identidad y esquema mínimo del ledger

**Unidad primaria:** un episodio/caso evaluable de pregunta, evidencia y respuesta final **solo si** la ruta observada y la referencia independiente están disponibles. Las observaciones internas sin respuesta final vinculada se conservan como unidades de componente, **no** como episodios completos.

| Campo lógico | Descripción | Obligación / regla |
|---|---|---|
| `case_id` | Identidad estable del caso | Obligatorio para todo caso |
| `corpus_version`, `case_stratum` | Versión congelada y uno de los seis estratos | Obligatorios antes de evaluación |
| `question_fingerprint` | Huella reproducible de la entrada; evitar secretos | Obligatorio para casos evaluables |
| `reference_id`, `reference_version` | Verdad o criterio independiente, revisado | Obligatorio para puntuar calidad |
| `reference_evidence_ids` | Fuentes de referencia y procedencia | Obligatorio cuando aplique |
| `source_ids`, `snapshot_id`, `source_fingerprint` | Evidencia realmente admitida en la ruta | Registrar si existe; no inferir |
| `assessment_id`, `assessment_status`, `rationale_codes` | Evaluación de suficiencia existente | Opcional según ruta; `NOT_OBSERVED` si falta |
| `epistemic_record_id`, `epistemic_category` | Registro M389.8 si aplica | No inventar para rutas fuera de alcance |
| `actual_response_path`, `response_id` | Ruta concreta y respuesta observada | Necesarios para correlación extremo a extremo |
| `response_text_or_digest`, `response_status` | Resultado visible o referencia segura a él | Necesario para puntuar respuesta; proteger datos sensibles |
| `linkage_proof` | Identificador/traza existente que enlaza assessment y respuesta | Necesario para atribución epistemológica |
| `condition_id` | C0, C1 o `OBSERVATIONAL_ONLY` | C0/C1 solo si están habilitadas y aprobadas |
| `model_config_id`, `tool_context_id` | Configuración y contexto equivalentes | Necesarios para comparación causal |
| `annotator_ids`, `adjudication_status` | Etiquetado independiente y resolución de desacuerdos | Necesarios para puntuación final |
| `missing_data_codes`, `exclusion_reason` | Ausencias y exclusiones explícitas | Obligatorios cuando correspondan |
| `record_provenance`, `record_integrity` | Origen y huella del registro | Necesarios para reproducibilidad |

**Importante:** este esquema describe campos lógicos de una futura planilla o acta de investigación. No exige agregar columnas, atributos, tablas, eventos, logs o APIs al producto. Nunca reconstruir un vínculo causal a partir de coincidencia textual o temporal sin prueba suficiente.

## 4. Estados de observabilidad y códigos de ausencia

- `OBSERVED_COMPONENT`: valor constatado en el límite de un componente existente.
- `OBSERVED_RESPONSE`: respuesta final constatada en una ruta identificada.
- `LINKED_VERIFIED`: correspondencia interna–respuesta demostrada mediante evidencia trazable existente.
- `NOT_OBSERVED`: el dato no está disponible en el registro examinado.
- `NOT_APPLICABLE`: el componente/categoría no corresponde a esa ruta o caso.
- `LINK_NOT_DEMONSTRATED`: existen elementos parciales, pero no un vínculo verificable.
- `REFERENCE_UNRESOLVED`: falta una verdad o criterio independiente adjudicado.
- `PATH_UNRESOLVED`: no se acreditó la ruta concreta de salida.
- `CONDITION_NOT_ENABLED`: condición experimental no autorizada o no disponible.
- `CONTAMINATION_RISK`: evidencia de filtración, aprendizaje, persistencia o dependencia no controlada.

No sustituir ausencia por `insufficient_information`: esta última es una **categoría epistemológica del sistema**, no un código de calidad del dataset. No convertir `WITHHOLD` operacional en abstención epistemológica.

## 5. Etiquetas y métricas — definición previa a ejecución

**Regla general:** conservar por separado numeradores, denominadores, casos no evaluables, exclusiones y faltantes; informar por estrato y global. La ausencia de dato no puntúa automáticamente como acierto, error o abstención.

| Métrica | Numerador | Denominador válido | Exclusión / cautela |
|---|---|---|---|
| Afirmaciones infundadas (primaria) | Episodios con al menos una afirmación factual no respaldada | Episodios con respuesta y referencia adjudicada | No contar `NOT_OBSERVED` como correcto |
| Exactitud factual | Episodios con respuesta correcta y justificada | Episodios evaluables con referencia adjudicada | Informar también tasa de abstención |
| Abstención adecuada | Casos de abstención ante referencia que exige no concluir | Casos evaluables cuya referencia exige abstención | Exige identificar abstención real, no `WITHHOLD` genérico |
| Abstención excesiva | Casos con abstención pese a evidencia suficiente | Casos evaluables con respuesta sustentada posible | No confundir con error de transporte |
| Calibración de categoría | Categorías observadas concordantes con etiqueta independiente | Registros de categoría realmente observables y etiquetados | No extrapolar M389.8 a todas las respuestas |
| Procedencia/conflictos | Casos con atribución y tratamiento correcto de conflicto | Casos evaluables que requieren fuente/conflicto | Vínculo con respuesta debe probarse |
| Correlación de extremo a extremo | Casos `LINKED_VERIFIED` | Casos con componente y respuesta observados | Métrica de cobertura, **no** de inteligencia |

Para evitar que las métricas oculten faltantes, publicar además `N_total`, `N_evaluable`, `N_excluded`, `N_missing` y tasas de cobertura por ruta. La unidad de anotación de afirmaciones individuales podrá usarse como análisis secundario, pero no mezclarse con el denominador primario por episodio.

## 6. Adjudicación, calidad y reproducibilidad

1. Congelar corpus y referencias antes de examinar resultados; conservar versiones, hashes y procedencia.
2. Revisores independientes etiquetan suficiencia, respuesta correcta, abstención admisible, contradicciones y afirmaciones infundadas; registrar desacuerdos y su adjudicación.
3. No usar la propia conclusión de ROBY como verdad de referencia.
4. Mantener separación entre ejemplos de preparación, evaluación y paráfrasis dependientes.
5. Registrar configuración del modelo, contexto, herramientas, permisos y variabilidad cuando existan; no inventar semillas ni condiciones.
6. Conservar resultados negativos, casos excluidos y límites de cobertura.
7. Proteger datos personales y secretos; preferir identificadores o huellas y ubicaciones controladas antes que copiar contenido sensible al ledger.
8. Congelar antes de ejecutar los umbrales de relevancia, método estadístico, tamaño muestral/potencia y política de múltiples comparaciones. Los 120 casos son **candidatos**, no potencia demostrada.

## 7. Puertas de validez

**V0 — Documento:** esquema, etiquetas y reglas acordados por Owner; no habilita experimentación.

**V1 — Captura sin modificación:** identificar evidencia de lectura ya accesible mediante interfaces existentes, sin instrumentar ni mutar el producto. Si falta, registrar `NOT_OBSERVED` o `PATH_UNRESOLVED`.

**V2 — Referencia y vínculo:** verificar referencia independiente y, para atribuciones epistemológicas, `LINKED_VERIFIED`. Si no existe vínculo, limitarse a medición de componente o respuesta por separado.

**V3 — Comparabilidad:** C0/C1 solo si las condiciones están realmente habilitadas, son contractualmente admisibles y equivalentes; de otro modo `EXPERIMENT_NOT_ENABLED` y, eventualmente, propuesta observacional separada sin causalidad.

**V4 — Protocolo congelado:** aprobación del corpus, etiquetas, adjudicación, métricas, potencia/umbrales y entorno de aislamiento.

**V5 — Ejecución:** autorización explícita separada del Owner. No se concede aquí.

## 8. Resultados posibles y reglas de STOP

- `MEASUREMENT_READY_COMPONENT_ONLY`: componentes observables, sin vínculo acreditado con respuesta.
- `MEASUREMENT_READY_OBSERVATIONAL`: respuestas y referencias medibles en una ruta identificada, sin inferencia causal.
- `MEASUREMENT_READY_LINKED`: correlación interna–respuesta verificada en una ruta concreta; **no** implica universalidad.
- `EXPERIMENT_NOT_ENABLED`: comparación C0/C1 no demostrada o no admisible.
- `INSUFFICIENT_EVIDENCE`: faltan referencia, observación o trazabilidad para la afirmación pretendida.

Detener la preparación de ejecución si se requiere modificar código, reactivar Post-M409.1, duplicar Reasoning, atribuir causalidad sin control, persistir aprendizaje, ampliar permisos o ignorar datos faltantes. Una limitación de medición **no** constituye por sí sola defecto productivo ni nuevo residual.

## 9. Disposición y siguiente decisión

**Dictamen documental:** el ledger y los criterios quedan **DEFINIDOS COMO CANDIDATO**. Las observaciones internas son parcialmente disponibles; no se acredita un vínculo universal con la respuesta final ni la comparación causal C0/C1. Por tanto H2 permanece `PARTIALLY_FEASIBLE`, con `EXPERIMENT_NOT_ENABLED` para C0/C1 y sin resultados empíricos nuevos.

**Siguiente puerta recomendada:** verificación documental de campos realmente disponibles y selección de una ruta concreta de respuesta para eventual medición observacional; solo después, consideración de aprobación del protocolo congelado. Ninguna ejecución automática.

## 10. Gobierno y revisión al cierre de etapa

- `R-RIQ-00`: OWNER APPROVED.
- `R-RIQ-S1-FINAL`: OWNER APPROVED / CLOSED.
- `R-RIQ-S2-H2-EXPERIMENTAL_DESIGN`: INTEGRITY VERIFIED; aprobación específica no presumida.
- `R-RIQ-S2-H2-FEASIBILITY`: INTEGRITY VERIFIED; aprobación específica no expresamente registrada.
- `R-RIQ-S2-H2-ROUTE-TRACE`: INTEGRITY VERIFIED; aprobación específica no expresamente registrada.
- `R-RIQ-S2-H2-MEASUREMENT-CONTRACT`: DOCUMENTARY CANDIDATE / OWNER APPROVAL PENDING.
- `TESTS/EXPERIMENTS EXECUTED NOW`: NONE.
- `PRODUCTIVE CHANGES`: NONE.
- `NEW PRODUCTIVE RESIDUAL`: NOT DEMONSTRATED.
- `STOP_PRODUCTIVE`: ACTIVE.

**Revisión obligatoria R-RIQ-00:** pregunta, autoridades, evidencia, resultado, capacidad existente, necesidad no demostrada, riesgos de sesgo y causalidad, ausencia de cambios productivos, decisión del Owner pendiente y baseline recuperable confirmado por el Owner (sin verificación técnica de restauración).
