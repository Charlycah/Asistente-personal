# ROBY XI.2 — M377: EXISTING PIPELINE EXECUTE/PROCESS CALL-SITE & RESPONSE PROVENANCE SEAM SELECTION — CONTRACT DECISION PRE-RED

Fecha: 2026-10-10. Baseline: `ROBY_XI_2_GOVERNED_MODEL_BACKEND_CANONICAL_AUTHORIZATION_TO_EXECUTION_SURGICAL_RECONCILIATION(1).zip`. Método: inspección estática de código, sin cambios ni ejecución de tests. Esta decisión no constituye certificación Owner.

## Dictamen

**CONTRACT DECISION: NO-GO para modificar M177 `execute()`, `OperationalResponse`, `UIResponse`, el adaptador protegido o publicar un perfil mutable global. PRE-RED HOLD para seleccionar un carrier productivo.** La ruta M177 `process()` conserva la preparación, pero ni la preparación ni el turno local transportan un perfil M377 tipado. El resultado de `execute()` intencionalmente expone solo la respuesta operativa. La ruta oficial Gateway consume un `LocalConversationTurn`, no directamente `GovernedConversationPipelineResult`.

## Evidencia de sitios de llamada

| Sitio | Código | Consecuencia |
|---|---|---|
| `core/governed_operational_conversation_pipeline/pipeline.py:68-74` | `execute()` crea `GovernedConversationPipelineRequest` y retorna `self.process(request).operational_response` | La interfaz `execute` no entrega `preparation` al llamador. No implica pérdida en el repositorio M177. |
| `core/desktop_runtime_integration/integration.py:143-165` | `self.pipeline.execute(owner=..., session_id=..., text=...)` | M176 consume `OperationalResponse`, sin evidencia de perfil M377. |
| `core/end_to_end_local_conversation/runtime.py:101-140` | crea `GovernedConversationPipelineRequest`, llama `composition.conversation_pipeline.process(request, now=now)` y convierte el resultado a `LocalConversationTurn` | Esta ruta conserva el resultado completo **hasta** la conversión al turno local. |
| `core/end_to_end_local_conversation/models.py:112-149` | `LocalConversationTurn.from_pipeline_result(...)` copia texto, estado, `pipeline_result_id`, `operational_response_id`, rutas y degradación | No copia `preparation` ni un perfil M377 tipado. Conserva identidad histórica de resultado. |
| `app/official_conversation_gateway.py:1115-1130, 1449-1468` | invoca `self._runtime.converse(...)` y luego lee opcionalmente `self._runtime.adaptive_personality_profile` | Lectura lateral sin asociación explícita con el `turn` devuelto. |
| `app/desktop_ui.py:212-219, 462-463, 495-496, 697-698` | lee tono del adaptador o perfil del runtime y llama `voice_reader.read(..., delivery_tone=...)` | No verifica que el tono corresponda al `turn` de esa respuesta. |

## Titularidad y procedencia

- `core/runtime_composition_root/preparation.py:394-407`: M55 produce personalidad estable; M377 produce `profile = adaptive_personality.adapt(stable, AdaptivePersonalityRequest())`; el perfil se proyecta a la solicitud de inferencia. **El perfil es local a `prepare()`**.
- `core/governed_operational_conversation_pipeline/pipeline.py:102-108`: la preparación se valida contra `owner`, `session_id`, `text`; `pipeline.py:164-177` construye `GovernedConversationPipelineResult` con `preparation`, `operational_response` y `response_origin`.
- `core/governed_operational_conversation_pipeline/models.py:248-268, 322-350`: resultado inmutable y `result_id` SHA-256 de la carga contractual; modificar su identidad histórica es un riesgo.
- `core/end_to_end_local_conversation/models.py:105-109`: `LocalConversationTurn.turn_id` también deriva de SHA-256 de la carga histórica.
- `ResponseOriginMetadata` describe procedencia de conocimiento/respuesta, **no es autoridad de personalidad ni carrier de tono**. No reutilizarlo semánticamente.
- La existencia de `GovernedConversationTurnIdentity` no demuestra que el perfil M377 esté asociado a su `turn_id` en esta ruta.

## Selección de seam — decisión comparativa

1. **No seleccionar `execute()`**: cambiar su retorno rompería consumidores M176 y el contrato histórico.
2. **No seleccionar `OperationalResponse`, `UIResponse` ni `ResponseOriginMetadata`**: son contratos de respuesta y procedencia, no titulares de personalidad; no mezclar semánticas.
3. **No seleccionar un atributo mutable global en runtime/adaptador**: riesgo de reutilización de tono entre turnos y sesiones; adaptador protegido por hash.
4. **Candidato de investigación, no autorización:** una proyección explícita por turno en el borde entre `GovernedConversationPipelineResult` y `LocalConversationTurn` / Gateway, siempre que pueda demostrarse una ruta permitida sin cambiar identidades históricas. El resultado M177 existente es el último objeto observado que conserva preparación y respuesta juntas; actualmente `preparation` carece del perfil tipado.
5. **Alternativa segura sin cambio:** mantener voz neutral/default cuando no exista evidencia de tono correlacionada al turno; la inferencia ordinaria conserva la expresión M377 ya proyectada en prompt.

## RED contractual mínimo propuesto (solo diseño)

Antes de autorizar cambios, pruebas RED deben demostrar: (a) el tono procede del perfil M377 del mismo turno y sesión; (b) dos turnos concurrentes/intercalados no cruzan tonos; (c) respuestas interceptadas, fallidas, degradadas y rutas de consola no heredan tono previo; (d) Gateway/voz no obtienen tono desde atributo global sin procedencia; (e) `execute()` sigue devolviendo `OperationalResponse`; (f) `UIResponse` y hash del adaptador no cambian; (g) `result_id`, `turn_id` y `response_id` mantienen sus reglas; (h) M390.5 no se conecta a la preparación ordinaria sin contrato posterior explícito; (i) ningún módulo/autoridad paralela.

Estas pruebas están **diseñadas, no escritas ni ejecutadas**. La viabilidad de un carrier concreto sigue pendiente de inspección de constructores/consumidores y tests protegidos del objeto `LocalConversationTurn` y del contrato Gateway→Desktop. No hay base suficiente para GREEN ni para un RED ejecutable.

## STOP y siguiente paso

**PRE-RED HOLD.** Recomendado: `M377 — LOCAL CONVERSATION TURN / OFFICIAL GATEWAY RETURN CONTRACT & NON-MUTATING EXPRESSION PROJECTION — RED FEASIBILITY AUDIT`. Revisar exhaustivamente tests y todos los constructores de `LocalConversationTurn` antes de seleccionar un carrier. Sin modificación de código, sin pruebas ejecutadas, sin nuevo ZIP. `MODEL_ACQUISITION` permanece NO-GO. Certificación Owner pendiente.
