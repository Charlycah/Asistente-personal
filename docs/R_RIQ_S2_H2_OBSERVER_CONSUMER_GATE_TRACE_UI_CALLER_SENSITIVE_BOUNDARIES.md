# ROBY XI.2 — R-RIQ-S2-H2-OBSERVER-CONSUMER-GATE-TRACE

**Existing UI/Caller Gates & Sensitive Output Boundaries (Static)**  
**Tipo:** acta científica candidata, inspección estática de solo lectura  
**Baseline:** `ultima version corregida(9).zip`  
**Gobierno:** `STOP_PRODUCTIVE: ACTIVE`; sin código, pruebas, ejecución ni experimentos.

## 1. Propósito y alcance

Rastrear consumidores existentes de `DevelopmentConsoleObserver` y `DevelopmentConsoleRenderer`, contrastar la exposición de datos sensibles con las fronteras documentadas de Desktop y diagnóstico, y determinar si existe una vía previamente autorizada para investigación H2. Esta acta no certifica comportamiento de una sesión real ni introduce autoridad nueva. No reabre certificaciones históricas.

## 2. Evidencia estática examinada

- `core/development_console_observability/observer.py`: `DevelopmentConsoleObserver` acepta un `EndToEndLocalConversation`; `runtime_observation`, `last_turn` y `turn_observation` leen historial, trazas y `composition.conversation_pipeline.repository.get(turn.pipeline_result_id)`.
- `core/development_console_observability/models.py`: `RuntimeObservation` contiene `owner` y `session_id`; `TurnObservation` incluye IDs de turno, traza, pipeline y respuesta operacional, además de `inference_prompt` e `inference_messages`.
- `core/development_console_observability/renderer.py`: `render_turn(..., reveal_prompt=False)` devuelve metadatos por defecto; con `True` emite contenido de prompt y mensajes. La opción controla presentación, no autorización del objeto ni acceso al runtime.
- `scripts/diagnostics/roby_conversational_e2e_harness.py`: construye `DevelopmentConsoleObserver(runtime)` y `DevelopmentConsoleRenderer()`, llama `app.controller.submit(prompt)` para cada caso, luego `observer.last_turn()` y `renderer.render_turn(..., reveal_prompt=reveal_prompt)`; `run_diagnostics` establece `reveal_prompt=True` por defecto y CLI `--metadata-only` lo desactiva. Es diagnóstico activo, no consulta pasiva. Escribe un TXT local; su cabecera indica sesiones diagnósticas aisladas y no modificación de `coowners-main`, afirmaciones no verificadas dinámicamente en esta etapa.
- `tests/test_m182_development_console_observability.py`, `tests/test_m224_3_llm_request_trace.py`, `tests/test_m225_2_structured_message_observability.py`, `tests/test_m225_3_provider_payload_message_verification.py`, `tests/test_post_m409_1_effective_provider_payload_observability_contract_v1.py`: consumidores de pruebas, no puertas de acceso productivo.
- `tests/architecture/test_m383_2_desktop_diagnostic_migration.py`: establece ausencia de importaciones del observador, renderer y `reveal_prompt` en `app/runtime_ui_adapter.py`, `app/desktop_ui.py` y `app/unified_brain.py`; comprueba que el diagnóstico Desktop no contenga contenido conversacional.
- `docs/M383_CONTROLLED_CONSOLE_RETIREMENT.md`, apartados M383.2, M383.13 y M383.17: Desktop conserva diagnóstico metadata-only, la revelación de prompts no se migró y la consola histórica fue retirada; no reactivar ni reconstruir ese acceso.
- `app/development_console.py`: comandos de doctor/configuración; no es un consumidor del observador de trazas.

## 3. Matriz de consumidores y puertas

| Superficie | Uso identificado | Control o límite estático | Dictamen H2 |
| --- | --- | --- | --- |
| `DevelopmentConsoleObserver` | Lee runtime/historial/trazas/repositorio inyectado | No se identifica comprobación de autorización por consulta dentro de este objeto | `INTERNAL_READ_ONLY / ACCESS_GATE_NOT_DEMONSTRATED` |
| `DevelopmentConsoleRenderer` | Proyecta observaciones en texto | `reveal_prompt=False` por defecto; `True` revela contenido | `PRESENTATION_FILTER_ONLY` |
| Harness diagnóstico | Crea sesiones diagnósticas y envía prompts nuevos | `--metadata-only` es opcional; default revela; archivo TXT local | `ACTIVE_DIAGNOSTIC / NOT_PASSIVE_RESEARCH_GATE` |
| Pruebas de observabilidad | Construyen y consultan objetos en tests | Contexto de pruebas; no acredita permisos de usuarios reales | `TEST_ONLY` |
| Desktop personal | Diagnóstico canónico metadata-only | M383 impide migrar revelación de prompts; suite arquitectónica controla ausencia de imports | `METADATA_ONLY / NOT_H2_RAW_DATA_GATE` |
| Consola histórica | Interfaz retirada | M383.17: retirada completada | `RETIRED / DO_NOT_REOPEN` |

## 4. Límites de información sensible

1. La presencia de `owner` y `session_id` es identidad de contexto, **no** comprobación de consentimiento ni de autorización.
2. `TurnObservation` conserva datos de prompt/mensajes incluso si el renderer no los imprime. El modo `reveal_prompt=False` no sanitiza necesariamente el objeto subyacente.
3. `reveal_prompt=True` y la salida local del harness permiten contenido sensible; no utilizar para investigación sin puerta autorizada, minimización y política de retención acreditadas.
4. El diagnóstico Desktop certificado como metadata-only no debe ampliarse para extraer prompts, respuestas o payloads; hacerlo contradiría la frontera M383.
5. El observador no demuestra acceso histórico persistente ni enlace universal entre evaluación de suficiencia H2 y respuesta final.

## 5. Límites de inferencia y resultados

- `OBSERVER_CONSUMERS_IDENTIFIED: YES_STATIC`
- `DESKTOP_METADATA_ONLY_BOUNDARY: DOCUMENTED_AND_TESTED_STATICALLY`
- `DIAGNOSTIC_HARNESS_PASSIVE: NO`
- `PROMPT_REVEAL_PRESENTATION_OPTION: CONFIRMED_STATICALLY`
- `PER_QUERY_AUTHORIZATION_IN_OBSERVER: NOT_DEMONSTRATED`
- `UPSTREAM_AUTHORIZATION_GATE_FOR_H2: NOT_DEMONSTRATED`
- `HISTORICAL_RESULTS_ACCESS: NOT_DEMONSTRATED`
- `EPISTEMIC_ASSESSMENT_TO_FINAL_RESPONSE_LINK: NOT_DEMONSTRATED`
- `C0_C1: EXPERIMENT_NOT_ENABLED`
- `OBSERVATIONAL_EXECUTION: NOT_AUTHORIZED`

No se concluye que exista vulnerabilidad; no se inspeccionaron exhaustivamente todos los mecanismos transversales de seguridad. Tampoco se concluye que el harness pueda usarse sin efectos: envía solicitudes y produce archivo. El análisis es estático sobre la versión ZIP indicada, no sobre el árbol local posterior.

## 6. Dictamen

**`EXISTING_OBSERVER_AND_DIAGNOSTIC_CONSUMERS_CONFIRMED / AUTHORIZED_NON_INVASIVE_H2_GATE_NOT_DEMONSTRATED / NOT_EXECUTION_READY`**.

La evidencia aconseja preservar la frontera metadata-only de Desktop y el carácter diagnóstico activo del harness. No crear observadores, endpoints, repositorios, rutas de acceso, módulos, gestores o autoridades paralelas. No modificar código ni ejecutar casos.

## 7. Próximo paso condicionado

Tras verificación SHA-256 y aprobación explícita del Owner, proponer `R-RIQ-S2-H2-AUTHORIZATION-EVIDENCE-RECONCILIATION — Existing Access Policy & Research Admission Evidence (Static)`: confrontar las políticas y autoridades existentes de permiso/consentimiento con la observación propuesta, sin inferir permisos por simple acceso a objetos. Si no se acredita puerta autorizada, declarar `INSUFFICIENT_EVIDENCE` y detener la habilitación observacional.

**Estado:** `DOCUMENT_PREPARED / OWNER_APPROVAL_PENDING / STOP_PRODUCTIVE_ACTIVE`.
