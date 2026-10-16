# ROBY XI.2 — M377 Pipeline Result / UI Response / Voice Turn-Correlation & Protected Contract Inventory — PRE-RED

**Estado:** AUDITORÍA ESTÁTICA; CONDITIONAL HOLD; sin RED autorizado. **Fuente:** ZIP integral `ROBY_XI_2_GOVERNED_MODEL_BACKEND_CANONICAL_AUTHORIZATION_TO_EXECUTION_SURGICAL_RECONCILIATION(1).zip`. No se ejecutaron pruebas ni se alteró código.

## Hallazgos confirmados

1. **Identidad canónica disponible pero no incorporada al transporte UI.** `core/governed_operational_conversation_pipeline/models.py:28-52` define `GovernedConversationTurnIdentity` (`conversation_id`, `request_id`, `turn_id`, `trace_id`) y función determinista a partir de owner/sesión/texto/fecha; la presencia del tipo no prueba que se use en la ruta vocal. `GovernedConversationPipelineResult` (`:248-267`) contiene `request`, `preparation`, ejecución, respuesta, `result_id`, etc., pero no perfil M377 ni un campo de identidad de turno. `result_id` se calcula y valida por hash (`:322-355`), por lo que alterar su payload puede romper identidad histórica.
2. **Preparación conserva la solicitud inferencial, no el perfil estructurado.** `GovernedConversationPreparation` (`models.py:176-203`) es `frozen=True`; tiene `owner`, `session_id`, `text`, `provider_route`, `inference_request`, `retrieval_plan` y evidencia de estrategia, sin perfil adaptativo. La proyección M377 al `system_prompt` ya existe en `core/runtime_composition_root/preparation.py`; no equivale a un transporte tipado para voz.
3. **Pipeline preserva preparación en el resultado.** `core/governed_operational_conversation_pipeline/pipeline.py:97-140,164-197` prepara, ejecuta, ensambla y devuelve `GovernedConversationPipelineResult(preparation=preparation, operational_response=response, ...)`. La ruta fallida fija `preparation=None` (`:150-163`). Esta conservación permite rastrear el request de inferencia, no extraer sin ambigüedad el perfil M377 original.
4. **M176 reduce el linaje.** `core/desktop_runtime_integration/integration.py:143-165` consume `pipeline.execute(...)`, tipado en `core/desktop_runtime_integration/models.py:134-142` como `OperationalResponse`, no como `GovernedConversationPipelineResult`. `DesktopRuntimeResult` (`models.py:73-86`) conserva `operational_response` o `console_turn` y su propio `result_id`, pero no `preparation`, perfil ni identidad canónica del turno. Además, existe una ruta de saludo por consola (`integration.py:125-142`) sin el mismo recorrido de preparación M377.
5. **Adaptador a UI reduce nuevamente.** `app/desktop_operational_adapter.py:34-54` retorna `UIResponse(text,status,session_id,needs_input)` sin tono o correlación de turno. `app/ui_adapter.py:11-16` define `UIResponse` congelado con esos cuatro campos. La sesión por sí sola no distingue respuestas concurrentes o sucesivas.
6. **Desktop lee estado lateral, no datos de respuesta.** `app/desktop_ui.py:212-219` busca `adapter.adaptive_delivery_tone` o `adapter.runtime._runtime.adaptive_personality_profile`; en `:458-463` lee el tono *después* de `submit_text` y lo pasa a `voice_reader.read(response, delivery_tone=...)`. El mismo patrón aparece en rutas visual y vocal (`:495-496`, `:696-698`). No hay comprobación de que el tono corresponda al `UIResponse` concreto. Un atributo mutable compartido implicaría riesgo de contaminación entre turnos/sesiones; esto es una **inferencia de riesgo**, no una concurrencia observada.
7. **Consumidor vocal existente.** `app/voice_output.py:244-251` recibe `UIResponse` y un `delivery_tone` separado; `:335-347` aplica valores de tono. No requiere añadir `delivery_tone` a `UIResponse`.
8. **Contratos protegidos.** `tests/architecture/test_r_mp_h4_voice_s2_canonical_adaptive_delivery_tone_productive_spoken_response_reachability_contract_red.py:49-96` exige que Gateway no contenga `adaptive_delivery_tone`, comprueba SHA-256 exacto del adaptador, prueba inyección sintética de perfil WARM a Desktop y prohíbe `delivery_tone` en la firma de `UIResponse`. La prueba de Gateway no es por sí sola una verificación de hash. Los tests de proyección M377 preservan el seam original `AdaptivePersonalityRequest()` por defecto y excluyen enriquecimientos directos en `preparation.py`.

## Matriz de correlación

| Frontera | Identidad | Perfil M377 | Dictamen |
|---|---|---|---|
| M377 → inferencia | request owner/sesión | texto de prompt | EXISTING |
| Preparación → resultado M177 | request + result_id | no campo tipado | PARTIAL |
| M177 → M176 | owner/sesión + respuesta operativa | no evidencia estructurada | NOT PROVEN |
| M176 → UIResponse | session_id | no campo | NOT PROVEN |
| UIResponse → lector de voz | response + tono lateral | lectura opcional global | UNCORRELATED |

## Conclusión contractual

**Residual candidato acotado:** ausencia de una asociación demostrable, por turno, entre el perfil M377 que alimentó la inferencia y el tono entregado al lector vocal. **No se demuestra ausencia del perfil en la inferencia**, ni justifica autoridad nueva. La identidad `GovernedConversationTurnIdentity` existe pero no puede declararse transportada hasta UI/voz por mera presencia del tipo. El `result_id` de M177 y M176 son identidades de resultados distintos; no deben confundirse con `turn_id`.

**No hacer:** mutar el adaptador protegido; añadir `delivery_tone` a `UIResponse`; almacenar un perfil mutable global como solución; reescribir hashes/result IDs; enriquecer `AdaptivePersonalityRequest()` contra el seam protegido; duplicar motor de personalidad.

**Próximo paso propuesto:** `M377 — CANONICAL PER-TURN EXPRESSION CARRIER OPTIONS & NEGATIVE CONTRACT TEST DESIGN — PRE-RED`. Primero inventariar si ya existe un carrier canónico de metadatos de respuesta fuera de UIResponse y del adaptador protegido; luego formular pruebas negativas de mezcla de sesiones/turnos, fallback neutral, rutas sin M377, voz deshabilitada y compatibilidad histórica. Solicitar aprobación Owner antes de cualquier RED/GREEN.

**STOP:** Sin código, sin ejecución de suite, sin certificación Owner; MODEL_ACQUISITION permanece UNMAPPED/NO-GO.
