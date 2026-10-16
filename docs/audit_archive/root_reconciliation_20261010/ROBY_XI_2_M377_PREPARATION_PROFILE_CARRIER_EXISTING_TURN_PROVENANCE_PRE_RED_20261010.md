# ROBY XI.2 — M377 Preparation Result Profile Carrier Contract Compatibility & Existing Turn Provenance Channel — PRE-RED

Fecha: 2026-10-10. Fuente: ZIP integral `ROBY_XI_2_GOVERNED_MODEL_BACKEND_CANONICAL_AUTHORIZATION_TO_EXECUTION_SURGICAL_RECONCILIATION(1).zip`. Método: lectura estática del código fuente; sin ejecución de pruebas ni cambios.

## Dictamen

**PRE-RED: CONDITIONAL HOLD.** El productor M377 existe y proyecta la personalidad en la solicitud de inferencia, pero no publica un perfil tipado en `GovernedConversationPreparation`. No se identificó en los objetos revisados un canal de procedencia expresiva correlacionado con la respuesta vocal. No autorizar RED hasta revisar compatibilidad de consumidores, tests y documentación contractual de cualquier nuevo campo.

## Evidencia comprobada

1. `core/runtime_composition_root/preparation.py:396-407`: `stable_personality.evaluate_turn(...)`, `adaptive_personality.adapt(stable, AdaptivePersonalityRequest())`, enriquecimiento de `inference_request`. La variable `profile` queda local a `prepare()`.
2. `core/runtime_composition_root/preparation.py:697-705`: retorno `GovernedConversationPreparation` con `owner`, `session_id`, `text`, `provider_route`, `inference_request`, `retrieval_plan`, `strategy_application_evidence`; sin perfil M377.
3. `core/governed_operational_conversation_pipeline/models.py:176-203`: `GovernedConversationPreparation` es `@dataclass(frozen=True)` con campos tipados, validación de identidad y referencias; no posee perfil ni identidad explícita de turno.
4. `core/governed_operational_conversation_pipeline/models.py:248-267`: `GovernedConversationPipelineResult` contiene `preparation` opcional, `operational_response`, `response_origin`, `response_path` y `result_id`; no perfil expresivo tipado. Su identidad se valida en `:322-325`.
5. `core/governed_operational_conversation_pipeline/pipeline.py:68-81`: `execute()` devuelve únicamente `self.process(request).operational_response`; `process()` conserva el resultado completo.
6. `core/end_to_end_local_conversation/runtime.py:127-140`: `converse()` llama a `process()` y construye `LocalConversationTurn.from_pipeline_result(...)`.
7. `core/end_to_end_local_conversation/models.py:47-64,111-149`: el turno local inmutable conserva `pipeline_result_id`, `operational_response_id`, respuesta, sesión, secuencia y su propio `turn_id`, pero no preparación ni perfil.
8. `core/governed_operational_conversation_pipeline/models.py:28-50`: `GovernedConversationTurnIdentity` tiene `conversation_id`, `request_id`, `turn_id`, `trace_id`, derivados de propietario, sesión, texto y marca temporal. **No es la misma construcción que** `LocalConversationTurn.turn_id` (`core/end_to_end_local_conversation/models.py:151+`). La mera coexistencia no demuestra un join estable.
9. `app/official_conversation_gateway.py:1464-1468`: lector opcional `runtime.adaptive_personality_profile`; `app/desktop_ui.py:212-219`: lector de `adapter.adaptive_delivery_tone` o de dicho perfil. Estos lectores no demuestran publicación productiva.
10. `tests/test_m177_governed_operational_conversation_pipeline.py`: constructor sintético de `GovernedConversationPreparation`; cualquier ampliación obligatoria del dataclass afectaría pruebas y potencialmente consumidores. El contrato original de proyección exige `AdaptivePersonalityRequest()` por defecto y prohíbe introducir señales M390.5 en `preparation.py` sin reconciliación explícita.

## Evaluación de compatibilidad de carrier

- **Campo opcional al final de `GovernedConversationPreparation`**: técnicamente plausible para preservar constructores posicionales/nominales y consumidores actuales, pero **no autorizado**. Exige revisar pruebas de igualdad, serialización, introspección, identidad, persistencia, contratos de arquitectura y tipo de perfil canónico. No se ha demostrado que baste para voz.
- **Añadir campo obligatorio o reordenar campos**: no viable sin migración contractual y pruebas.
- **Reutilizar `strategy_application_evidence`**: rechazado; autoridad de estrategia cognitiva, no perfil expresivo.
- **Reutilizar `response_origin` o identificadores SHA-256**: rechazado; la procedencia de respuesta y la identidad histórica no son transportadores de personalidad.
- **Mutar atributos de runtime/adaptador**: rechazado; riesgo de fuga entre turnos/sesiones, además de protecciones del adaptador.
- **Reconstruir el perfil leyendo el `system_prompt`**: rechazado; sería frágil y violaría procedencia tipada.
- **Extensión no mutante, inmutable y por turno en canal ya autorizado**: opción conceptual prioritaria, **pendiente de identificar un canal real** y un consumidor autorizado.

## Requisitos para cualquier RED posterior

1. Verificar que un `profile` tipado conserva la misma instancia/valores producidos por M377, sin segundo cálculo ni segunda autoridad.
2. Probar el enlace inequívoco de propietario, sesión, solicitud y turno; definir explícitamente si se usa `GovernedConversationTurnIdentity`, `LocalConversationTurn.turn_id` o una correspondencia contractual entre ambos.
3. Cubrir turnos simultáneos/intercalados, respuestas tardías, interceptores, degradación y ausencia de preparación M377. Sin perfil verificable, voz neutra/segura; nunca reutilizar el tono previo.
4. Preservar los hashes de `GovernedConversationPipelineResult` y `LocalConversationTurn`, el retorno de `execute()`, `Gateway.submit()`, `UIResponse`, y el hash protegido del adaptador.
5. Revisar inventarios, registros de capacidades, documentación maestra y tests arquitectónicos antes de modificar cualquier contrato.
6. Definir RED contractual negativo mínimo, obtener aprobación del Owner, ejecutar GREEN quirúrgico y suite local; no declarar certificación anticipada.

## Próximo paso propuesto

**M377 — PREPARATION CARRIER FIELD-COMPATIBILITY / RESULT-ID INVARIANCE & GATEWAY CONSUMER CONTRACT MATRIX — RED CONTRACT DESIGN (HOLD)**. Primero construir matriz exhaustiva de constructores, consumidores, serializadores y tests que dependen de los dataclasses y las identidades. Después elegir el punto de proyección y formular RED sin escribir código de producto.

Estado: sin código modificado, sin pruebas ejecutadas, sin ZIP nuevo; `MODEL_ACQUISITION = NO-GO`; certificación Owner pendiente.
