# ROBY XI.2 — R-RIQ-S2-H2-OBSERVER-BOUNDARY-ASSESSMENT
## Existing Observer Scope & Non-Invasive Research Eligibility (Static)

**Clase:** acta científica candidata, documental y estática.  
**Baseline:** `ultima version corregida(9).zip` (lectura de fuentes, sin ejecución de ROBY).  
**Gobierno:** una autoridad por capacidad; reutilización antes que duplicación; `STOP_PRODUCTIVE: ACTIVE`.  
**Estado:** DOCUMENT PREPARED / OWNER APPROVAL PENDING.

## 1. Objeto y alcance

Evaluar el alcance del observador ya existente, sus datos, fronteras de sesión/propietario, mecanismos de revelación de información y elegibilidad para una investigación H2 no invasiva. No se ejecutan solicitudes, harness, pruebas, scripts del producto ni experimentos. No se modifica código.

Esta acta continúa las etapas R-RIQ-S2-H2-READ-CALLER-TRACE, ACCESS-BOUNDARY-RECONCILIATION, EXISTING-ACCESS-TRACE, OBSERVATIONAL-READINESS, FIELD-MAPPING y MEASUREMENT-CONTRACT; no reabre sus certificaciones.

## 2. Fuentes estáticas inspeccionadas

- `core/development_console_observability/observer.py`: `DevelopmentConsoleObserver`, `runtime_observation`, `last_turn`, `turn_observation`.
- `core/development_console_observability/models.py`: `RuntimeObservation`, `TurnObservation`.
- `core/development_console_observability/renderer.py`: `DevelopmentConsoleRenderer.render_runtime`, `render_turn`.
- `core/end_to_end_local_conversation/models.py`: `EndToEndLocalConversationConfig`, `LocalConversationTurn`, `from_pipeline_result`.
- `core/end_to_end_local_conversation/runtime.py`: acceso a `history`, `traces`, composición y procesamiento.
- `app/development_console.py`: utilidades de diagnóstico; no debe confundirse con la autoridad del observador.

## 3. Superficie observacional realmente definida

`DevelopmentConsoleObserver(runtime)` conserva referencia a una instancia `EndToEndLocalConversation` entregada por el llamador. `runtime_observation()` obtiene propietario, sesión, estado, inicio, número de turnos/trazas y nombres de módulos compuestos. `last_turn()` consulta el historial de esa instancia; `turn_observation(sequence)` busca un turno por secuencia y su traza, y, cuando existe `bootstrap.composition`, usa `composition.conversation_pipeline.repository.get(turn.pipeline_result_id)`.

`TurnObservation` incluye identidad (`turn_id`, `trace_id`, `pipeline_result_id`, `operational_response_id`), estado, módulos y eventos; indicadores de proveedor, recuperación, red y mutación; métricas de contexto; proveedor/modelo y metadatos de payload. También puede contener `inference_prompt` e `inference_messages`, potencialmente sensibles.

**Límite:** `TurnObservation` no declara `response_text`, evaluación epistemológica H2, ground truth independiente ni una asociación universal evaluación–respuesta. El turno subyacente `LocalConversationTurn` sí modela `response_text`, `owner`, `session_id` y `response_path`, pero su presencia en el modelo no demuestra que el observador los publique ni que exista una interfaz externa autorizada.

## 4. Frontera de propietario y sesión

`RuntimeObservation` informa `owner` y `session_id` desde `bootstrap.config`. `LocalConversationTurn` conserva `owner` y `session_id`. Sin embargo, el código del observador inspeccionado **no muestra un parámetro de identidad del solicitante, un control de autorización por llamada, ni una validación explícita de que el turno recuperado pertenezca a la identidad de quien consulta**. El alcance efectivo depende de la instancia de runtime suministrada y de las garantías de construcción/entrega de esa instancia.

**Dictamen:** `OWNER_SESSION_METADATA: AVAILABLE`; `CALLER_AUTHORIZATION_ENFORCEMENT: NOT_DEMONSTRATED`; `EXTERNAL_RESEARCH_ACCESS: NOT_AUTHORIZED_BY_THIS_EVIDENCE`.

La ausencia de una comprobación en este componente no prueba una vulnerabilidad del sistema completo: la autorización podría residir en capas superiores no acreditadas en este recorte. No se propone remediación productiva sin reconciliación gobernada y autorización.

## 5. Revelación de prompts y riesgo de exposición

`DevelopmentConsoleRenderer.render_turn(item, reveal_prompt=False)` devuelve por defecto un resumen de metadatos. Con `reveal_prompt=True`, incorpora líneas de `inference_prompt` y contenidos de `inference_messages`. El parámetro es una **opción de presentación**, no un control de autorización demostrado. Un consumidor con acceso directo al objeto `TurnObservation` también podría leer esos campos sin usar el renderer.

**Consecuencia científica:** no se debe interpretar `reveal_prompt=False` como sanitización, anonimización ni autorización. Cualquier eventual uso de datos requeriría frontera gobernada y minimización explícita, sin exponer prompts ni mensajes privados por defecto.

## 6. Alcance temporal, completitud y pasividad

El observador consulta `runtime.history` y `runtime.traces` de la instancia recibida. En `turn_observation`, si no existe composición o resultado de repositorio, parte de los campos se deriva de metadatos vacíos o valores predeterminados. Esto **no demuestra** ausencia real de ejecución de proveedor, memoria, herramientas o trazas: puede ser falta de dato disponible.

`EndToEndLocalConversationConfig` define opciones de persistencia (`persist_turns`, `persist_traces`) y rutas de journal/traza. La existencia de estas opciones no prueba que el observador permita recuperar resultados históricos después de reiniciar ni que el repositorio del pipeline esté rehidratado.

Las llamadas del observador inspeccionadas son proyecciones/consultas y no invocan `conversation_pipeline.process`; pero ello no habilita ejecutar el runtime ni su harness. Tampoco se certifica aquí ausencia absoluta de efectos colaterales en todo el sistema o en dependencias externas.

## 7. Matriz de elegibilidad H2

| Requisito | Evidencia | Dictamen |
|---|---|---|
| Observador canónico existente | `DevelopmentConsoleObserver` | CONFIRMED_STATICALLY |
| Lectura de turno y resultado en instancia viva | `history`, `traces`, `repository.get` | CONDITIONAL |
| Metadatos owner/session | `RuntimeObservation`, `LocalConversationTurn` | AVAILABLE |
| Control explícito de autorización por consulta | No acreditado en observador | NOT_DEMONSTRATED |
| Acceso científico externo legítimo | No acreditado | NOT_DEMONSTRATED |
| Texto final en `TurnObservation` | No figura en su contrato | NOT_AVAILABLE_IN_OBSERVER_MODEL |
| Texto de respuesta en modelo de turno | `LocalConversationTurn.response_text` | AVAILABLE_IN_UNDERLYING_MODEL |
| Identificadores de correlación | `turn_id`, `pipeline_result_id`, `operational_response_id` | AVAILABLE |
| Correlación evaluación epistemológica H2–respuesta | No acreditada | NOT_DEMONSTRATED |
| Referencia factual independiente | No aportada | NOT_PREPARED |
| Recuperación histórica de repositorio tras reinicio | No acreditada | NOT_DEMONSTRATED |
| Protección de prompts por `reveal_prompt=False` | Sólo presentación | NOT_AN_AUTHORIZATION_GATE |
| Ejecución de experimento C0/C1 | No autorizada ni habilitada | EXPERIMENT_NOT_ENABLED |

## 8. Dictamen

**`OBSERVER_PRESENT / RESEARCH_ACCESS_NOT_DEMONSTRATED / NOT_EXECUTION_READY`.**

La observabilidad interna existente constituye una base útil para estudiar factibilidad. No constituye, por sí sola, un canal de investigación autorizado, un corpus científico, una garantía de privacidad o un enlace causal con H2. No se declara bug, regresión, nueva capacidad requerida ni mejora de inteligencia demostrada.

## 9. Condiciones para la próxima revisión documental

Antes de plantear cualquier evaluación, identificar estáticamente los **consumidores de `DevelopmentConsoleObserver` y de `DevelopmentConsoleRenderer`**, los puntos de construcción/entrega de `EndToEndLocalConversation`, y los controles de identidad, sesión, permisos y revelación de prompts **en las capas superiores existentes**. Distinguir `NOT_DEMONSTRATED` de `ABSENT`; no construir una ruta paralela ni ejecutar consultas reales.

**Próxima etapa candidata:** `R-RIQ-S2-H2-OBSERVER-CONSUMER-GATE-TRACE — Existing UI/Caller Gates & Sensitive Output Boundaries (Static)`; su inicio requiere integridad documental y aprobación del Owner.

## 10. STOP y certificación

- `STOP_PRODUCTIVE: ACTIVE`.
- `PRODUCTIVE_CHANGES: NONE`.
- `TESTS_EXECUTED: NONE`.
- `EXPERIMENTS_EXECUTED: NONE`.
- `C0/C1: EXPERIMENT_NOT_ENABLED`.
- `OWNER_APPROVAL: PENDING`.
- Esta acta no certifica un runtime ni modifica el estado de auditorías previas.
