# ROBY XI.2 — M377 Canonical Preparation Result & Turn-Identity Transport Reconciliation — PRE-RED

**Fecha:** 2026-10-10  
**Fuente:** `ROBY_XI_2_GOVERNED_MODEL_BACKEND_CANONICAL_AUTHORIZATION_TO_EXECUTION_SURGICAL_RECONCILIATION.zip` (ZIP integral recibido; inspección estática de código).  
**Tipo:** reconciliación PRE-RED; no implementación, no certificación Owner.

## 1. Evidencia directa

1. `core/runtime_composition_root/preparation.py:336-342` define `GovernedRuntimePreparation.prepare(request, *, now=None, reasoning_now=None)` y retorna `GovernedConversationPreparation`.
2. `preparation.py:394-407`: construye `inference_request`; evalúa M55; M377 produce una variable local `profile` mediante `adaptive_personality.adapt(stable, AdaptivePersonalityRequest())`; el perfil se usa para enriquecer la solicitud de inferencia. La variable local no se publica explícitamente como atributo de runtime.
3. `preparation.py:697-705`: el retorno incluye `owner`, `session_id`, `text`, `provider_route`, `inference_request`, `retrieval_plan`, `strategy_application_evidence`; no incluye el perfil M377 ni un identificador de turno explícito.
4. `core/governed_operational_conversation_pipeline/models.py:176-203`: `GovernedConversationPreparation` es un dataclass congelado con esos campos; valida identidad de owner/session y correspondencia de owner con route/plan. No declara `adaptive_personality_profile`, `delivery_tone` ni `turn_id`.
5. `core/governed_operational_conversation_pipeline/pipeline.py:68-81,97-105`: `execute` construye una solicitud de pipeline y `process` prepara el turno; `last_result` accede a un repositorio de resultados. No se ha demostrado que el repositorio preserve un perfil M377 por turno.
6. `app/desktop_ui.py:212-219`: el consumidor vocal busca `adapter.adaptive_delivery_tone`, o bien `adapter.runtime._runtime.adaptive_personality_profile.delivery_tone`. No vincula explícitamente la lectura con la identidad del turno.
7. `app/official_conversation_gateway.py:1464-1468`: lee opcionalmente `self._runtime.adaptive_personality_profile`; la lectura no demuestra un productor ni transporte por turno.
8. `preparation.py:195-205`: existe `build_governed_conversation_turn_identity(request, now)` en otra ruta cognitiva. Su existencia **no demuestra** que esa identidad se asocie al perfil M377 o llegue a voz.

## 2. Diferencia entre existencia y alcance

**EXISTING:** M377 y M55 producen expresión en el `system_prompt`; Desktop y Gateway conocen consumidores opcionales; el pipeline posee identidad owner/session y una construcción de identidad de turno en rutas específicas.

**UNVERIFIED:** enlace de la variable local `profile` con un transporte autorizado por turno; propagación hasta Desktop/voz en una ejecución real; conservación de identidad bajo concurrencia; integridad del vínculo respuesta-perfil; posible canal alternativo existente.

**DUPLICATE-RISK:** nuevo gestor de personalidad, nuevo adaptador vocal o publicación de un atributo mutable global sin aislamiento por turno.

## 3. Residual candidato, no certificado

`M377_CANONICAL_TURN_PROFILE_TO_EXISTING_VOICE_CONSUMER_PROVENANCE`

La hipótesis acotada es que la información expresiva que M377 ya calcula para inferencia no dispone de un canal explícito, seguro y verificable hasta el consumidor de voz. La ausencia de un campo en `GovernedConversationPreparation` es evidencia concreta, pero no prueba por sí sola la ausencia de todo canal indirecto.

## 4. Contratos protegidos y prohibiciones

- No enriquecer `AdaptivePersonalityRequest()` ni incorporar M390.5 al seam ordinario sin reconciliación contractual.
- No alterar por defecto `LLMRequest`, `UIResponse`, gateway, Desktop ni adaptador protegido por hash.
- No inferir tono a partir del texto del `system_prompt` ni recalcular M377 en la UI.
- No guardar el último perfil en un atributo global compartido sin identidad de turno y pruebas de concurrencia.
- Preservar el fallback neutral y el único cerebro integrado.

## 5. Verificaciones pendientes antes de RED

1. Inspeccionar exhaustivamente `GovernedConversationPipelineResult`, `OperationalResponse`, `UIResponse` y todos los puertos de conversión hasta voz.
2. Seguir `build_governed_conversation_turn_identity` y los identificadores realmente disponibles en el ciclo de vida de respuesta.
3. Inventariar pruebas de hash/inmutabilidad y restricciones de los seams de Gateway, adaptador, Desktop y voz.
4. Buscar productores indirectos/dinámicos y rutas de transporte ya existentes para `adaptive_personality_profile` y `adaptive_delivery_tone`.
5. Determinar un único punto de integración permitido y un contrato de pertenencia a turno/sesión, incluyendo concurrencia y fallbacks.
6. Obtener aprobación explícita del Owner del residual exacto antes de RED ejecutable.

## 6. Dictamen

**PRE-RED RECONCILIATION: CONDITIONAL HOLD.** Producción M377 y proyección a inferencia demostradas; transporte de perfil por turno hasta voz no demostrado. No se justifica código nuevo todavía. No se modificaron archivos del baseline ni se ejecutó pytest/ruff en esta auditoría. `MODEL_ACQUISITION` continúa `UNMAPPED / NO-GO`.

**Próxima auditoría recomendada:** `M377 — PIPELINE RESULT / UI RESPONSE / VOICE TURN-CORRELATION & PROTECTED CONTRACT INVENTORY — PRE-RED`.
