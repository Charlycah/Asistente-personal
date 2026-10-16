# ROBY XI.2 — M377 Local Conversation Turn / Official Gateway Return Contract & Non-Mutating Expression Projection — RED Feasibility Audit

**Fecha:** 2026-10-10  
**Estado:** Auditoría estática / PRE-RED; **RED HOLD**.  
**Baseline:** `ROBY_XI_2_GOVERNED_MODEL_BACKEND_CANONICAL_AUTHORIZATION_TO_EXECUTION_SURGICAL_RECONCILIATION(1).zip`. Sin cambios de código ni ejecución de pruebas.

## Evidencia verificada

1. `core/runtime_composition_root/preparation.py:394-407`: `prepare()` obtiene perfil M377 con `AdaptivePersonalityRequest()` y lo proyecta en `inference_request`; no lo entrega como dato tipado al resultado de preparación.
2. `core/end_to_end_local_conversation/runtime.py:127-140`: `converse()` obtiene el resultado completo de `conversation_pipeline.process()` y construye `LocalConversationTurn.from_pipeline_result()`. El resultado completo existe temporalmente en el ámbito local.
3. `core/end_to_end_local_conversation/models.py:47-65,111-149`: `LocalConversationTurn` es `dataclass(frozen=True)`, contiene IDs de resultado y respuesta, pero no perfil/tono. `from_pipeline_result()` copia datos de respuesta, identidad y procedencia operacional; no copia `preparation` ni un perfil adaptativo.
4. `core/end_to_end_local_conversation/models.py:151-165`: `turn_id` se calcula como SHA-256 de campos establecidos, incluidos texto, respuesta, IDs y fecha. No debe modificarse el payload histórico para introducir tono.
5. `app/official_conversation_gateway.py:1115-1130,1523-1530`: la ruta ordinaria invoca `self._runtime.converse(...)`; `submit()` retorna el `turn` sin una envoltura expresiva tipada.
6. `app/official_conversation_gateway.py:1454-1492`: el Gateway obtiene opcionalmente `self._runtime.adaptive_personality_profile` para evidencia relacional; no lo correlaciona con el `turn_id` retornado.
7. `app/desktop_ui.py:212-219,449-463`: Desktop toma el tono del atributo opcional `adapter.adaptive_delivery_tone` o del perfil opcional del runtime; después llama a `voice_reader.read(response, delivery_tone=...)`. Es una lectura lateral, no una evidencia vinculada a `LocalConversationTurn`.
8. `app/ui_adapter.py:11-16,23-53`: `UIResponse` es inmutable y no contiene tono; el adaptador genérico transforma `UserResponse` a `UIResponse`. Esta ruta no debe confundirse con todas las rutas de integración del Gateway.

## Evaluación de puntos de unión

| Punto | Evidencia | Dictamen |
|---|---|---|
| Dentro de `prepare()` | Perfil M377 disponible localmente | Autoridad de cálculo existente; no hay carrier tipado de salida |
| `EndToEndLocalConversationRuntime.converse()` tras `process()` | Resultado completo y secuencia del turno disponibles | **Único punto de coexistencia temporal demostrado**, pero el perfil tipado no está en `result.preparation` |
| `LocalConversationTurn.from_pipeline_result()` | Construye turno inmutable y `turn_id` histórico | No extender sin auditar serialización, consumidores y hashes |
| `OfficialConversationGateway.submit()` | Recibe y devuelve turno | Punto de retorno existente; no recupera perfil M377 correlacionado |
| Desktop / voz | Consume `UIResponse` y tono lateral | No hay unión por `turn_id` demostrada; riesgo de contaminación entre turnos |

## Factibilidad de proyección no mutante

**No demostrada aún.** La coexistencia de `result` y la construcción del turno en `runtime.converse()` es un *join-point de control*, no un carrier de perfil autorizado. Un perfil extraído del texto del prompt sería una reconstrucción no canónica; un atributo compartido de runtime/adaptador sería mutable y no ligado al turno. No se autoriza ninguna de esas alternativas.

Para abrir RED hacen falta: (a) demostrar un canal tipado, ya existente, para obtener el perfil desde `prepare()` sin romper contratos; (b) identificar una ruta de respuesta/voz que transporte metadatos por turno sin cambiar `UIResponse`, `turn_id`, `result_id` ni adaptador protegido; (c) probar correlación exacta y aislamiento entre sesiones, respuestas tardías, errores, interceptores y rutas sin M377; (d) contrastar tests de hash, persistencia y contratos de voz antes de modificar firmas.

## Pruebas negativas propuestas (no implementadas)

- Intercalado A/B: un turno A no consume tono de B.
- Respuesta tardía: no consume el último tono global.
- Interceptor sin M377: tono predeterminado, sin reutilización residual.
- `turn_id` y `pipeline_result_id`: mismos payloads e identidades históricas.
- `UIResponse`: mismos campos; adaptador protegido: mismos bytes.
- Perfil ausente o inconsistente: ninguna inferencia por lectura del `system_prompt`.
- `Gateway.submit()` mantiene el tipo y comportamiento de retorno en todas sus rutas.

## Dictamen y próximo paso

**CONDITIONAL HOLD / NO RED EJECUTABLE.** No hay justificación para crear un manager, un registro global, un nuevo cerebro, ni una autoridad expresiva paralela. El candidato más cercano es la ventana local `process()` → `from_pipeline_result()`, pero falta un perfil tipado en ese punto. Próxima revisión acotada: **`M377 — PREPARATION RESULT PROFILE CARRIER CONTRACT COMPATIBILITY & EXISTING TURN PROVENANCE CHANNEL — PRE-RED`**, con inventario de serialización, tests y extensiones admisibles antes de diseñar un RED.

`MODEL_ACQUISITION`: **NO-GO**. Certificación Owner: pendiente.
