# ROBY XI.2 — M377 Gateway→Desktop/Voice Same-Turn Expression Delivery Channel & Protected Consumer Contract — FINAL RED GATE

Fecha: 2026-10-10. Alcance: inspección estática del ZIP integral `ROBY_XI_2_GOVERNED_MODEL_BACKEND_CANONICAL_AUTHORIZATION_TO_EXECUTION_SURGICAL_RECONCILIATION(1).zip`. Sin cambios ni ejecución de pruebas.

## Decisión
**FINAL RED GATE: NO-GO para RED productivo completo; sí procede un RED de caracterización contractual, sujeto a aprobación del Owner.** El canal de entrega de tono del mismo turno no está demostrado ni autorizado en los contratos inspeccionados. No debe declararse GREEN por el éxito de una prueba con perfil sintético.

## Evidencia concreta

1. `core/runtime_composition_root/preparation.py`: M377 produce un perfil y proyecta sus atributos al prompt, sin exponer el perfil como dato tipado en `GovernedConversationPreparation`.
2. `core/end_to_end_local_conversation/runtime.py:137-140,156-163`: `converse()` construye `LocalConversationTurn` desde el resultado completo, lo persiste y devuelve el turno; no añade perfil expresivo.
3. `core/end_to_end_local_conversation/models.py:47-64,112-140`: `LocalConversationTurn` es inmutable, contiene `turn_id`, `pipeline_result_id`, `operational_response_id` y respuesta, pero no perfil M377.
4. `app/official_conversation_gateway.py:1115-1130,1523-1530`: el Gateway delega en `runtime.converse()` y retorna el turno; otras ramas del Gateway también producen turnos sin preparación M377. `app/official_conversation_gateway.py:1464-1467` lee opcionalmente `runtime.adaptive_personality_profile`, sin probar su asignación productiva.
5. `app/desktop_ui.py:212-219`: `_adaptive_delivery_tone()` prioriza `adapter.adaptive_delivery_tone`, luego `adapter.runtime._runtime.adaptive_personality_profile.delivery_tone`. **No recibe `response` ni `turn_id`**. `app/desktop_ui.py:462-463,495-496,697-698`: el tono se lee después de `submit_text()` y se pasa a `voice_reader.read(response, delivery_tone=...)`.
6. `tests/architecture/test_r_mp_h4_voice_s2_canonical_adaptive_delivery_tone_productive_spoken_response_reachability_contract_red.py:69-86`: prueba WARM con runtime sintético y fallback None con adaptador legado; no verifica correlación causal entre perfil real y respuesta del mismo turno.
7. El mismo contrato, líneas 49-58, prohíbe el token `adaptive_delivery_tone` en el código Gateway; líneas 61-65 exigen SHA-256 exacto del adaptador `2afb8629a78800c64932e289a905a098bb1a32bd5952ec152b204e42924a08e1`; líneas 89-96 prohíben `delivery_tone` en `UIResponse` y autoridad/recomputación adaptativa en Desktop.

## Riesgo causal
El consumidor vocal lee un atributo lateral del runtime/adaptador sin asociarlo a la identidad de la respuesta. Aunque una asignación futura del perfil fuese encontrada, la lectura actual no prueba seguridad ante sesiones intercaladas, respuestas tardías o ramas Gateway que no pasen por M377. No se afirma que tales fallos ocurran actualmente: la propiedad requerida no está demostrada.

## Matriz de decisiones

| Ruta | Viabilidad contractual |
|---|---|
| Añadir `delivery_tone` a `UIResponse` | Rechazada por contrato |
| Modificar adaptador protegido | Rechazada por hash |
| Añadir autoridad de personalidad a Desktop | Rechazada |
| Modificar `Gateway.submit()` para publicar tono global | Rechazada; contrato y riesgo de intercalado |
| Extender `GovernedConversationPreparation` con perfil opcional inmutable | Condicionada; no alcanza a voz por sí sola |
| Transportar perfil correlacionado por turno a consumidor existente | Objetivo deseado, canal aún no identificado ni certificado |
| Fallback `None` cuando falta evidencia del mismo turno | Compatible con prueba de adaptador legado |

## Pruebas RED de caracterización propuestas (sin implementar)
- Perfil real de M377 del turno A no puede ser aplicado al turno B de otra sesión.
- Respuesta tardía de A no adopta el perfil de B.
- Una rama Gateway sin preparación M377 produce `delivery_tone=None` salvo evidencia canónica explícita.
- Coincidencia obligatoria de identidad/procedencia de turno antes de proyectar tono; no basta un atributo global.
- Prueba productiva end-to-end: preparación M377 real → resultado → Gateway/adapter → Desktop → `VoiceResponseReader.read` con perfil exacto, sin simulación del productor.
- Preservar SHA-256 del adaptador, firma de `UIResponse`, `LocalConversationTurn.turn_id`, `GovernedConversationPipelineResult.result_id` y semántica de `execute()`.
- Verificar todas las ramas de `DesktopConversationController` que llaman a `voice_reader.read`.

## Gate de salida
Para autorizar RED quirúrgico productivo deben identificarse: (a) un carrier por turno aceptado por contrato; (b) el join de identidad entre resultado y consumidor; (c) la ruta para las tres llamadas vocales; (d) ausencia de colisión con protecciones; (e) autorización expresa del Owner. Hasta entonces **HOLD / NO-GO**, sin implementar un campo huérfano en preparación.

## Siguiente paso recomendado
`M377 — SAME-TURN EXPRESSION DELIVERY CONTRACT CHARACTERIZATION RED — OWNER DECISION`: redactar pruebas RED mínimas para demostrar la ausencia de correlación y compatibilidad de consumidores sin tocar código productivo, y someter el alcance al Owner. No introducir módulos paralelos, mutación compartida ni adquisición neuronal.
