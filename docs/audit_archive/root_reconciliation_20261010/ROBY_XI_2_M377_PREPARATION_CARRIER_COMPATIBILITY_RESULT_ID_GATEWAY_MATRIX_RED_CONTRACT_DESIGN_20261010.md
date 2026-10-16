# ROBY XI.2 — M377 Preparation Carrier Field-Compatibility / Result-ID Invariance & Gateway Consumer Contract Matrix — RED CONTRACT DESIGN

Fecha: 2026-10-10. Alcance: auditoría estática del ZIP `ROBY_XI_2_GOVERNED_MODEL_BACKEND_CANONICAL_AUTHORIZATION_TO_EXECUTION_SURGICAL_RECONCILIATION(1).zip`. No se modificó código ni se ejecutó pytest/ruff. **Diseño contractual, no RED ejecutado ni certificación Owner.**

## Evidencia inspeccionada

- `core/governed_operational_conversation_pipeline/models.py:176-203`: `GovernedConversationPreparation` es `@dataclass(frozen=True)` con siete campos, de los cuales `retrieval_plan` y `strategy_application_evidence` tienen default. Constructor productivo `core/runtime_composition_root/preparation.py:697-705`; constructores adicionales en `tests/test_m177_governed_operational_conversation_pipeline.py` y `tests/test_post_m409_1_conditional_action_routing_e2e.py`.
- `core/runtime_composition_root/preparation.py:395-407`: `AdaptivePersonalityRequest()` sin argumentos, adaptación M377 y proyección al `inference_request`; `:697-705` devuelve preparación sin perfil.
- `core/governed_operational_conversation_pipeline/models.py:248-325`: resultado M177 inmutable y validaciones de linaje; `:327-...` `_identity_payload()` incluye `preparation.provider_route.route_id` pero no serializa todos los campos de preparación. La invarianza de `result_id` **se puede formular**, pero debe demostrarse con pruebas de regresión reales.
- `core/end_to_end_local_conversation/models.py:47-109,111-165`: turno local inmutable, `turn_id` calculado por `_identity_payload`; `from_pipeline_result` copia `pipeline_result_id` y `operational_response_id`, no el perfil M377.
- `core/end_to_end_local_conversation/runtime.py:127-163`: la ruta local utiliza `process()`, construye `LocalConversationTurn` y lo retorna.
- `app/official_conversation_gateway.py:1464-1468`: lectura opcional de `self._runtime.adaptive_personality_profile`; `:1530` retorna `turn`.
- `app/desktop_ui.py:212-219`: tono del adaptador o lectura lateral del perfil runtime; `:462-463,495-496,697-698`: pasa tono a `voice_reader.read`.

## Matriz de compatibilidad y decisión

| Superficie | Hipótesis de cambio | Invariante obligatoria | Estado |
|---|---|---|---|
| `GovernedConversationPreparation` | Añadir al final `adaptive_personality_profile: AdaptivePersonalityProfile \| None = None` (nombre/tipo a verificar) | Los siete parámetros actuales, constructor posicional y keyword, congelamiento y ausencia de perfil deben conservar comportamiento | **Candidata condicionada; no autorizada** |
| `GovernedRuntimePreparation.prepare` | Retener perfil local ya calculado y proyectarlo al resultado | Una sola evaluación M377; `AdaptivePersonalityRequest()` permanece default; no M390.5 en seam protegido | **Diseño hipotético** |
| M177 `result_id` | No tocar `_identity_payload()` | Identidad idéntica con/sin carrier para mismos insumos originales | **Protegida; requiere RED** |
| M180 `LocalConversationTurn.turn_id` | No tocar `_identity_payload()` | Hash idéntico y `from_pipeline_result` compatible | **Protegida; requiere RED** |
| `Gateway.submit` | Conservar retorno `LocalConversationTurn` | No ampliar firma ni sustituir retorno; no leer perfil de otra solicitud | **Protegido** |
| Adaptador local | Ningún cambio | Hash SHA-256 protegido, misma semántica | **Protegido** |
| `UIResponse` | Ningún campo de tono | Estructura y serialización invariantes | **Protegido** |
| Desktop/Voz | Sólo evidencia del mismo turno | Sin reutilización de tono, sin estado global mutable | **No demostrado** |
| Interceptor / degraded / withheld | Perfil ausente o no aplicable | Fallback neutral/actual, no herencia del turno anterior | **RED negativo requerido** |

## Decisión del carrier

Un campo opcional añadido **al final** de `GovernedConversationPreparation` es una alternativa razonable para el tramo preparación→M177. **No es una solución integral**: `LocalConversationTurn` no retiene el objeto de preparación y el Gateway devuelve el turno local. La entrega del carrier al consumidor vocal no queda resuelta. No se autoriza agregar un campo hasta identificar un enlace completo sin mutación compartida y sin alterar contratos protegidos.

El tipo concreto de perfil debe obtenerse del módulo M377 y verificarse contra sus restricciones de importación, circularidad y serialización. No inferir que un nuevo campo puede entrar automáticamente en hashes, igualdad, representaciones públicas o serialización.

## RED contractual propuesto (diseño; NO implementado)

1. **Constructor compatible:** los tres constructores identificados siguen funcionando; construcción sin perfil produce `None`; no se permite perfil mal tipado si se decide introducir validación.
2. **Invarianza M177:** para una misma solicitud, respuesta y procedencia, el `result_id` no cambia al variar únicamente un eventual carrier expresivo. Verificar el payload y el hash, no solo que el constructor acepte el campo.
3. **Invarianza M180:** `turn_id`, `pipeline_result_id`, `operational_response_id` y el retorno de `from_pipeline_result` permanecen idénticos ante variación exclusiva del carrier.
4. **Invarianza Gateway/UI:** firma y tipo de retorno de `Gateway.submit`, esquema `UIResponse`, contrato del adaptador y hashes protegidos sin cambios.
5. **Sin segunda autoridad:** el perfil proviene exclusivamente de M377; ninguna segunda llamada a `adapt`, parsing del `system_prompt` o modulación M390.5 introducida en `preparation.py`.
6. **Dos turnos intercalados:** A/WARM y B/CAREFUL no cruzan perfiles aunque B finalice primero; verificar `owner`, `session_id` y una identidad de turno inequívoca.
7. **Respuesta tardía:** la salida vocal de A no recibe el tono de B ni el último atributo global del runtime.
8. **Ausencia de preparación:** interceptor, degradación, ruta de consola o respuesta sin M377 no heredan tono previo.
9. **Identidad incompatibile:** un carrier de otra solicitud/sesión no puede aplicarse a la respuesta actual; rechazo o fallback explícito.
10. **Regresión de voz:** la ruta existente sigue leyendo tono inyectado legítimamente y conserva fallback cuando no hay tono.
11. **Regresión documental:** pruebas de arquitectura que exigen `AdaptivePersonalityRequest()` default y prohíben tokens M390.5 permanecen GREEN.
12. **Pruebas locales:** `ruff check .`, tests contractuales específicos, `pytest -q` y baseline de calidad, únicamente tras autorización.

## Criterio para salir de HOLD

Antes de escribir RED ejecutable: (a) localizar un canal existente **del mismo turno** entre `LocalConversationTurn`/Gateway y Desktop/Voz; (b) documentar los contratos exactos de su consumidor y verificar si está protegido; (c) decidir si el campo en preparación aporta valor a ese canal sin extender innecesariamente los modelos; (d) autorización Owner para un RED acotado. Si no existe canal compatible, **no** resolver con atributo global ni reabrir interfaces históricas por conveniencia.

**Estado:** CONTRACT DESIGN COMPLETED / RED EXECUTABLE HOLD / NO GREEN / OWNER CERTIFICATION PENDING / MODEL_ACQUISITION NO-GO.
