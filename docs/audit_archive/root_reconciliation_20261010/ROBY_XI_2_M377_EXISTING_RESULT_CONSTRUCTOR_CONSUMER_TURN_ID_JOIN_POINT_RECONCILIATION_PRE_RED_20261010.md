# ROBY XI.2 — M377: Existing Result Constructor/Consumer & Turn-ID Join-Point Contract Reconciliation — PRE-RED

**Fecha:** 2026-10-10  
**Baseline:** `ROBY_XI_2_GOVERNED_MODEL_BACKEND_CANONICAL_AUTHORIZATION_TO_EXECUTION_SURGICAL_RECONCILIATION(1).zip`  
**Método:** inspección estática de código y contraste con informe PRE-RED anterior; sin ejecución de tests, sin modificaciones.

## 1. Evidencia confirmada con archivos y líneas

1. `core/runtime_composition_root/preparation.py:394-407`: construye `LLMRequest`, calcula personalidad estable M55 y perfil adaptativo M377 usando `AdaptivePersonalityRequest()`; enriquece el request de inferencia. El perfil es variable local. `:697-705`: construye y devuelve `GovernedConversationPreparation` sin perfil tipado ni identidad explícita de turno.
2. `core/governed_operational_conversation_pipeline/models.py:176-184`: `GovernedConversationPreparation` es dataclass congelada con owner, session_id, text, route, inference_request, retrieval_plan y strategy_application_evidence. `:248-267`: `GovernedConversationPipelineResult` conserva `request`, `preparation`, `operational_response`, origen, ruta y demás datos. `:327-354`: identidad histórica `result_id` calculada de un payload definido; no cambiarlo incidentalmente.
3. `core/governed_operational_conversation_pipeline/pipeline.py:97-115,164-197`: `process()` obtiene la preparación, ejecuta el proveedor, construye resultado completo, lo registra y devuelve. `:68-74`: **`execute()` devuelve solo `self.process(request).operational_response`**; este borde elimina del valor retornado el acceso a `preparation` y a los metadatos propios del resultado completo.
4. `core/governed_operational_conversation_pipeline/pipeline.py:199-238,240-265`: rutas interceptor e inactiva construyen resultados con `preparation=None`; no se puede presumir perfil M377 en todas las respuestas.
5. `core/governed_operational_conversation_pipeline/models.py:28-52`: `GovernedConversationTurnIdentity` y `build_governed_conversation_turn_identity()` existen con conversation_id, request_id, turn_id, trace_id, derivados de owner, sesión, texto y timestamp. En el escaneo de archivos Python de producto **no se encontró invocación** de ese constructor; solo aparece su definición. Esto no prueba que no exista otra identidad canónica en otra ruta, pero impide afirmar que esta identidad se use actualmente como join-key del perfil.
6. `core/desktop_runtime_integration/integration.py:143-165,167-214`: `DesktopRuntimeIntegration` llama a `self.pipeline.execute(owner,session_id,text)` y convierte un `OperationalResponse` en `DesktopRuntimeResult`. `core/desktop_runtime_integration/models.py:73-86,112-131`: el resultado Desktop conserva `operational_response` pero no el resultado completo de M177 ni perfil M377, y tiene su propia identidad histórica.
7. `app/ui_adapter.py:11-16` y `app/runtime_ui_adapter.py:159-200`: `UIResponse` no contiene perfil ni tono, y el adaptador expone rutas `submit_text` y `submit_voice` que retornan `UIResponse`. Se observaron múltiples constructores en adaptadores y tests; cambiar el contrato tendría alcance amplio.
8. `app/desktop_ui.py:212-219,449-463,487-496,696-698`: Desktop busca `adaptive_delivery_tone` en adaptador o `adaptive_personality_profile` en runtime después de obtener la respuesta; entrega el tono opcional a `voice_reader.read`. No hay comprobación visible de `turn_id`/`request_id` en esa lectura.
9. `app/official_conversation_gateway.py:1464-1468`: el Gateway lee opcionalmente `runtime.adaptive_personality_profile`; no constituye prueba de publicación productiva. Escaneo de `.py` bajo `app/` y `core/`: las únicas referencias productivas a ese nombre fueron este lector y el de Desktop; no apareció una asignación explícita.
10. Escaneo de constructores de producto: `GovernedConversationPreparation(` 1 constructor productivo en `preparation.py`; `GovernedConversationPipelineResult(` 3 constructores productivos en `pipeline.py`; `DesktopRuntimeResult(` 8 en `desktop_runtime_integration/integration.py`; `UIResponse(` múltiples en adaptadores y aplicaciones. Los tests también construyen instancias sintéticas. Estos conteos describen el baseline inspeccionado, no un inventario semántico de todas las llamadas indirectas.

## 2. Join-point: qué coexiste realmente

| Punto | Perfil M377 | Identidad canónica de turno | Respuesta | Accesible a Desktop/Voz | Dictamen |
|---|---|---|---|---|---|
| `GovernedRuntimePreparation.prepare()` durante evaluación | Sí, variable local | Request owner/session/text y timestamp, sin join tipado al perfil | Aún no | No directamente | No es join-point completo |
| `GovernedConversationPreparation` | Solo expresión en `inference_request` | Owner/session/text; no `turn_id` | No | Indirectamente, vía pipeline | No es carrier tipado |
| `GovernedConversationPipelineResult` de `process()` | Preparación con prompt enriquecido, no perfil tipado | Request y `created_at`, sin `GovernedConversationTurnIdentity` almacenada | Sí | No mediante `execute()` | Join de preparación y respuesta, **no** de perfil tipado/identidad explícita |
| `execute()` → `OperationalResponse` | No tipado | No clave M177 visible en resultado | Sí | Sí, hacia Desktop | **Borde de pérdida de contexto de preparación** |
| `DesktopRuntimeResult` | No | Request/session e identidad propia | Sí | Sí | Sin perfil M377 |
| `UIResponse` → `VoiceResponseReader` | No | Session opcional, sin clave de turno | Sí | Sí | Sin correlación causal |
| Lectura lateral Desktop/Gateway | Potencial, atributo opcional no publicado explícitamente | Sin cotejo con respuesta | Sí, separadamente | Sí | No segura como carrier por turno |

**Conclusión:** no se identificó un punto existente que reúna *perfil M377 tipado + identidad canónica efectiva del mismo turno + respuesta consumida por voz*. El primer resultado que reúne preparación y respuesta es `GovernedConversationPipelineResult`, pero no reúne el perfil tipado ni lo transporta por el contrato `execute()` actual. No se autoriza añadir campos por inferencia.

## 3. Restricciones y compatibilidad

- Mantener M55/M377 como autoridades canónicas y el `AdaptivePersonalityRequest()` original; M390.5 no debe introducirse en el seam restringido.
- No añadir `delivery_tone` a `UIResponse`; no editar adaptador protegido por SHA-256 sin autorización y reconciliación contractual.
- No cambiar hashes/`result_id` históricos de M177/M176, ni sus rutas `INTERCEPTOR`, `DEGRADED`, `WITHHELD`, consola, ni su comportamiento sin preparación.
- No publicar perfil en un atributo global mutable: respuestas tardías, sesiones intercaladas y reentrancia podrían contaminar el tono.
- No reconstruir perfil analizando texto o `system_prompt`; pierde procedencia.
- La identidad `GovernedConversationTurnIdentity` es existente, pero **no se ha demostrado su adopción** por el recorrido productivo inspeccionado.

## 4. Pruebas RED negativas a preparar (no implementadas)

1. Perfil del turno A no se aplica a respuesta B aunque compartan sesión; y viceversa bajo intercalación.
2. Perfil de sesión A no se aplica a sesión B; la respuesta tardía conserva su propia identidad.
3. Sin `preparation` o sin M377, voz neutra/segura, sin reutilizar perfil anterior.
4. Identidad incompatible (`conversation_id`, `request_id`, `turn_id`) no puede unirse a respuesta ajena.
5. Los resultados de `process()`, `execute()`, M176 y `UIResponse` mantienen sus contratos históricos, hashes y payloads protegidos.
6. `submit`, `submit_with_visual_companion`, `submit_voice` y respuestas directas de seguridad se comportan correctamente sin depender de atributos globales.
7. Prueba causal real: perfil calculado por M377 para un turno → misma respuesta → mismo tono vocal; sin fixture que inyecte manualmente el atributo de runtime.
8. No se crea una segunda autoridad de personalidad ni un sistema de identidad paralelo.

## 5. Decisión de preparación contractual

**PRE-RED: COMPLETADO. RED EJECUTABLE: HOLD.** Hay evidencia suficiente de que `execute()` no transporta el resultado completo y de que la lectura lateral vocal no está correlacionada por turno. No hay todavía evidencia suficiente para seleccionar un carrier implementable que respete los contratos protegidos. La brecha demostrada es de **disponibilidad de metadatos y trazabilidad causal**, no prueba de fallo de la personalidad en la inferencia ordinaria.

**Siguiente paso recomendado:** `M377 — EXISTING PIPELINE EXECUTE/PROCESS CALL-SITE & RESPONSE PROVENANCE SEAM SELECTION — CONTRACT DECISION PRE-RED`. Investigar las llamadas reales y contratos de `execute()`/`process()` y la conversión al gateway/UI, y decidir explícitamente si existe un seam autorizado o si corresponde cerrar con HOLD hasta aprobación Owner. No RED/GREEN automático.

**Sin código modificado, sin tests ejecutados, sin ZIP integral nuevo. `MODEL_ACQUISITION = NO-GO`; certificación Owner pendiente.**
