# ROBY XI.2 — R-RIQ-S2-H2-EXISTING-ACCESS-TRACE
## Existing Read-Only Result Access Verification

**Clase:** acta científica candidata, inspección estática de interfaces existentes.  
**Base inspeccionada:** `ultima version corregida(9).zip`, prefijo `ultima version corregida/`.  
**Antecedente:** `R_RIQ_S2_H2_OBSERVATIONAL_READINESS_CANONICAL_RESPONSE_ROUTE.md`, aprobado por Owner.  
**Restricción:** `STOP_PRODUCTIVE: ACTIVE`; sin ejecución, instrumentación, cambios de código ni tests.

## 1. Pregunta y criterio

Determinar si el código ya contiene contratos de lectura de resultados de conversación operacional, distinguirlos de un acceso autorizado a datos reales, y establecer si permiten una medición científica no invasiva. La presencia de una interfaz no demuestra que esté expuesta, conectada a una sesión real o disponible tras reinicios.

## 2. Evidencia directa inspeccionada

### E1. Repositorio de resultados de conversación

`core/governed_operational_conversation_pipeline/models.py`, líneas 358–378 del ZIP: `GovernedConversationPipelineRepository(Protocol)` define `add(result)`, `get(result_id)` y `list_all()`. `InMemoryGovernedConversationPipelineRepository` implementa esas operaciones sobre `_items: dict[str, GovernedConversationPipelineResult]`. `get` y `list_all` son operaciones de consulta en la implementación inspeccionada; `add` es mutadora y queda fuera del alcance de observación.

**Dictamen de campo:** `READ_INTERFACE_EXISTS`; `PERSISTENT_RESULT_ACCESS: NOT_DEMONSTRATED`.

### E2. Acceso desde la instancia de pipeline

`core/governed_operational_conversation_pipeline/pipeline.py`, líneas 37–66: `GovernedOperationalConversationPipeline.__init__` admite `repository: GovernedConversationPipelineRepository | None`; si no se suministra, instancia `InMemoryGovernedConversationPipelineRepository`. `last_result` consulta `repository.list_all()` y devuelve el último resultado disponible, si existe. Es acceso a la instancia en memoria, no evidencia de una API pública, almacenamiento persistente ni una sesión activa disponible al investigador.

**Dictamen:** `INSTANCE_SCOPED_READ: AVAILABLE_CONDITIONALLY`; `EXTERNAL_READ_ENTRYPOINT: NOT_DEMONSTRATED`.

### E3. Modelo del resultado y correlación operacional interna

`core/governed_operational_conversation_pipeline/models.py`, líneas 248–355: `GovernedConversationPipelineResult` contiene `request`, `status`, `operational_response`, `created_at`, `result_id`, `response_path`, `response_origin`, `rationale`, y otros campos de ejecución. El `result_id` se deriva de un payload que incluye `operational_response.response_id` y la ruta de respuesta (líneas 327–355). Esto aporta correlación estructural **entre resultado del pipeline y respuesta operacional**; no prueba un enlace con un assessment de suficiencia epistemológica H2 ni con toda salida final de ROBY.

**Dictamen:** `PIPELINE_TO_OPERATIONAL_RESPONSE_LINK: AVAILABLE_IN_MODEL`; `H2_ASSESSMENT_TO_FINAL_RESPONSE_LINK: NOT_DEMONSTRATED`.

### E4. Repositorio de respuestas ensambladas

`core/operational_response_assembly/models.py`, líneas 196–216: `OperationalResponseRepository(Protocol)` declara `add`, `get`, `list_all`; la implementación `InMemoryOperationalResponseRepository` consulta su diccionario en memoria. `core/operational_response_assembly/assembler.py`, líneas 20–32 y 194–196: `OperationalResponseAssembler` acepta un repositorio opcional y guarda las respuestas ensambladas mediante `repository.add(response)`.

**Dictamen:** `ASSEMBLED_RESPONSE_READ_INTERFACE_EXISTS`; `PERSISTENT_OR_EXTERNALLY_ACCESSIBLE_HISTORY: NOT_DEMONSTRATED`.

## 3. Matriz de cobertura de acceso

| Pregunta | Dictamen | Alcance |
|---|---|---|
| ¿Hay métodos existentes de consulta por ID? | `AVAILABLE` | Repositorios en memoria de pipeline y assembler |
| ¿Hay enumeración de resultados? | `AVAILABLE` | `list_all` sobre una instancia concreta |
| ¿Existe consulta del último resultado? | `CONDITIONAL` | `last_result` requiere instancia y datos cargados |
| ¿Se conserva `result_id` junto a `response_id`? | `AVAILABLE` | Modelo de resultado y payload de identidad |
| ¿Existe acceso autorizado a instancias reales en ejecución? | `NOT_DEMONSTRATED` | No acreditado por contratos estáticos |
| ¿Se conservan resultados tras reinicio? | `NOT_DEMONSTRATED` | Implementaciones inspeccionadas son in-memory |
| ¿Hay endpoint o exportación científica read-only? | `NOT_DEMONSTRATED` | No acreditado por los archivos examinados |
| ¿Se enlaza evaluación H2 a respuesta final? | `NOT_DEMONSTRATED` | Sin correlación probada |
| ¿Puede ejecutarse C0/C1? | `NO` | `EXPERIMENT_NOT_ENABLED` |

**Alcance negativo:** `NOT_DEMONSTRATED` no significa inexistencia en todo el producto; significa que esta inspección no lo acredita. No se certificó exhaustividad de todas las integraciones, configuraciones, rutas ni despliegues.

## 4. Condiciones para una futura lectura observacional

Antes de cualquier ejecución se requerirá: (a) autorización explícita del Owner para un procedimiento concreto; (b) identificación de la instancia real y su autoridad; (c) prueba documental de que la consulta no invoca `process`, `execute`, `assemble` ni `add`; (d) delimitación de datos personales/sensibles y minimización; (e) procedencia, timestamp y correspondencia `result_id` ↔ `response_id`; (f) ground truth independiente; (g) registro de faltantes sin imputación; (h) decisión separada de habilitación experimental. Nada de ello queda autorizado por esta acta.

## 5. Dictamen

`EXISTING_READ_ONLY_REPOSITORY_INTERFACES: CONFIRMED_STATICALLY`  
`IN_MEMORY_INSTANCE_ACCESS: CONDITIONAL`  
`REAL_RUNTIME_RESULT_ACCESS: NOT_DEMONSTRATED`  
`PERSISTENCE: NOT_DEMONSTRATED`  
`H2_ASSESSMENT_TO_FINAL_RESPONSE_LINK: NOT_DEMONSTRATED`  
`OBSERVATIONAL_EXECUTION_READINESS: NOT_READY`  
`C0/C1: EXPERIMENT_NOT_ENABLED`  
`PRODUCTIVE_RESIDUAL: NOT_DEMONSTRATED`  
`STOP_PRODUCTIVE: ACTIVE`

La nueva evidencia **refina** el acta anterior: ya no es correcto decir sin matices que no existen mecanismos de consulta; existen interfaces de lectura **en memoria**, pero no está probado el acceso a resultados reales ni la aptitud para un experimento. No hay autorización para crear repositorios, endpoints, exportadores, hooks, instrumentación o autoridades paralelas.

## 6. Próximo paso propuesto, sujeto a aprobación

`R-RIQ-S2-H2-ACCESS-BOUNDARY-RECONCILIATION — Runtime Wiring & Authorized Read Boundary (Static)`.

Objetivo: rastrear, sin ejecutar nada, dónde se construyen e inyectan los repositorios y el pipeline, y si una ruta ya gobernada expone consultas autorizadas. Antes de iniciarlo, incorporar este documento a `docs/`, verificar SHA-256 y obtener aprobación del Owner.

**Estado:** `DOCUMENT PREPARED / OWNER APPROVAL PENDING`.
