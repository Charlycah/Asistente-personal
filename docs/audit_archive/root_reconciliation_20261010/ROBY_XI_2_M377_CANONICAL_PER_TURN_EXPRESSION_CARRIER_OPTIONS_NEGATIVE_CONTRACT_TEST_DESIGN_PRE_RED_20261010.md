# ROBY XI.2 — M377: Canonical Per-Turn Expression Carrier Options & Negative Contract Test Design — PRE-RED

**Fecha:** 2026-10-10  
**Alcance:** auditoría estática y diseño de pruebas; sin cambios de código ni ejecución de tests.  
**Baseline examinado:** `ROBY_XI_2_GOVERNED_MODEL_BACKEND_CANONICAL_AUTHORIZATION_TO_EXECUTION_SURGICAL_RECONCILIATION(1).zip`.

## Evidencia positiva

- `core/runtime_composition_root/preparation.py:394-407`: se construye el `LLMRequest`, se evalúa M55 y se calcula M377 con `AdaptivePersonalityRequest()`; el perfil se usa para enriquecer la inferencia, pero permanece local.
- `core/governed_operational_conversation_pipeline/models.py:176-184`: `GovernedConversationPreparation` es inmutable y carece de perfil tipado o identificador explícito del turno.
- `core/governed_operational_conversation_pipeline/models.py:28-46`: existe `GovernedConversationTurnIdentity` con `conversation_id`, `request_id`, `turn_id` y `trace_id`. No debe duplicarse.
- `core/governed_operational_conversation_pipeline/models.py:248-265, 327-354`: `GovernedConversationPipelineResult` conserva `preparation`, respuesta y `result_id` cuyo hash depende de campos establecidos; una ampliación requiere revisar compatibilidad e identidad.
- `app/ui_adapter.py:11-16`: `UIResponse` inmutable solo incluye texto, estado, sesión y necesidad de entrada.
- `app/desktop_ui.py:212-219, 449-463, 487-496`: el tono se lee lateralmente del adaptador o runtime **después** de `submit_text`, sin verificar una clave de turno. Hay múltiples caminos de emisión vocal.
- `app/voice_output.py:244-251, 335-347`: el lector acepta `delivery_tone` y proyecta valores conocidos. Es consumidor, no productor M377.

## Opciones de transporte — comparativa

| Opción | Ventaja | Riesgo/contrato | Estado |
|---|---|---|---|
| A. Campo en `GovernedConversationPreparation` | Transporta el perfil junto a la preparación y queda asociado al resultado | Modifica dataclass canónica; verificar constructores, snapshots, tests y rutas sin preparación; identidad de turno no aparece en este tipo | **Candidata condicionada** |
| B. Evidencia tipada en `GovernedConversationPipelineResult` | Correlación con respuesta de pipeline | Afecta constructor/contratos y potencialmente `result_id`; no asegura llegada a Desktop/voz | **No preferir sin inventario adicional** |
| C. Sobre o proyección por-turno en canal existente de resultado hacia Desktop | Puede preservar `UIResponse` y adaptador protegido si ya existe un canal tipado y autorizado | **No se demostró** un canal existente que lleve el perfil hasta voz; inventarlo sería arquitectura paralela | **Investigación prioritaria, no implementable aún** |
| D. Atributo global mutable `runtime.adaptive_personality_profile` | Encaja con el lector lateral actual | Contaminación entre sesiones, respuestas tardías y reentrancia; falta vinculación al turno | **RECHAZADA** |
| E. `adapter.adaptive_delivery_tone` mutable | Encaja con la precedencia de Desktop | Adaptador protegido por hash; riesgo de tono obsoleto y compartido | **RECHAZADA** |
| F. Agregar `delivery_tone` a `UIResponse` | Interfaz directa | Contrato de voz protege su ausencia | **RECHAZADA** |
| G. Analizar el `system_prompt` o el texto final para recuperar tono | Evita campo explícito | Deriva tono de contenido, pierde procedencia M377 y puede exponer instrucciones | **RECHAZADA** |

**Selección:** no hay una opción GREEN demostrada. La preferencia conceptual es un transporte inmutable asociado al turno a través de una ruta canónica existente, sin estado compartido. Antes del RED, verificar quién construye y consume cada resultado y si una ruta autorizada preserva identidad y procedencia hasta la voz.

## Diseño de RED contractual negativo (no implementado)

1. **Aislamiento de sesiones:** dos solicitudes intercaladas A/WARM y B/CAREFUL deben emitir sus propios tonos, nunca el último valor global.
2. **Aislamiento de turnos de una sesión:** una respuesta tardía del turno 1 no puede heredar el perfil del turno 2.
3. **Sin preparación:** respuestas `INTERCEPTOR`, `DEGRADED` o `WITHHELD` sin perfil M377 no deben reutilizar tono previo; fallback neutro, sin inventar perfil.
4. **Identidad no coincidente:** perfil con `turn_id`, `request_id` o `conversation_id` ajeno debe rechazarse/no aplicarse; no basta comparar solo `session_id`.
5. **Inmutabilidad:** la evidencia asociada a un turno no debe cambiar después de producirse, incluso si se procesa otro turno.
6. **Proveniencia canónica:** solo se acepta tono derivado del `AdaptivePersonalityAuthority` de M377 y de la preparación pertinente; no se introduce motor paralelo.
7. **Compatibilidad de contratos:** `UIResponse` sigue sin `delivery_tone`; se conserva la identidad/hash del adaptador protegido; no se modifica `AdaptivePersonalityRequest()` por defecto ni se acopla M390.5 al seam restringido.
8. **Identidad histórica de resultados:** `result_id` existente no debe cambiar por incorporar metadatos expresivos fuera de su identidad contractual, salvo autorización y reconciliación explícita.
9. **Sin perfil:** ausencia de dependencias M55/M377 produce comportamiento seguro, sin inferencia heurística del tono.
10. **Vías vocales múltiples:** verificar `submit`, `submit_with_visual_companion` y `submit_voice` y las rutas directas de voz/seguridad; ninguna debe recibir perfil de otra respuesta.
11. **No filtración de instrucciones:** el perfil interno no debe imprimirse en el texto visible ni exponerse por el lector vocal.
12. **Determinismo y concurrencia:** la resolución de tono se asocia a la respuesta correcta bajo intercalación/reentrancia, sin consultar un puntero global al final de `submit_text`.

## Precondiciones para abrir RED ejecutable

- Inventariar todos los constructores/consumidores de `GovernedConversationPreparation`, `GovernedConversationPipelineResult`, `DesktopRuntimeResult`, `UIResponse` y la ruta Gateway→Desktop.
- Identificar el primer punto **existente y permitido** donde coexisten identidad canónica del turno, perfil M377 y resultado consumible, o demostrar que no existe.
- Contrastar las restricciones de hash del adaptador, tests de voz y proyección M377 con documentación posterior de precedencia.
- Definir un único contrato mínimo, sus aserciones negativas y una prueba causal de integración de turno real; obtener autorización Owner antes de GREEN.

## Dictamen

**PRE-RED COMPLETADO / RED EXECUTABLE: HOLD.** El residual de transporte está razonablemente localizado, pero no existe evidencia suficiente para escoger un carrier sin riesgo de alterar contratos protegidos. **No código, no tests ejecutados, no ZIP nuevo, no autoridad adicional. `MODEL_ACQUISITION`: NO-GO.**

**Siguiente paso:** `M377 — EXISTING RESULT CONSTRUCTOR/CONSUMER & TURN-ID JOIN-POINT CONTRACT RECONCILIATION — PRE-RED`.
