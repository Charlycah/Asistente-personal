# ROBY XI.2 — M377 Turn-Scoped Profile Lifecycle & Protected Gateway/Adapter/Voice Contract Audit

**Fecha:** 2026-10-10  
**Estado:** auditoría estática PRE-RED; **pendiente de certificación Owner**  
**Baseline examinado:** `ROBY_XI_2_GOVERNED_MODEL_BACKEND_CANONICAL_AUTHORIZATION_TO_EXECUTION_SURGICAL_RECONCILIATION(1).zip`  
**Cambios de producto:** ninguno. **Ejecución de pruebas:** no realizada en este incremento.

## 1. Alcance y método

Se contrastaron directamente dentro del ZIP el productor canónico de personalidad (`core/runtime_composition_root/preparation.py`), el lector del gateway (`app/official_conversation_gateway.py`), el consumidor Desktop (`app/desktop_ui.py`), la salida de voz (`app/voice_output.py`) y los tests arquitectónicos de proyección M377 y alcance vocal. Se efectuó una búsqueda textual de referencias a `adaptive_personality_profile`, `adaptive_delivery_tone` y `delivery_tone` en archivos Python de producto y tests. La ausencia de una asignación textual no excluye por sí sola mecanismos dinámicos.

## 2. Cadena causal observada

1. `preparation.py:394-407`: construye `inference_request`, evalúa M55 con `request.text`, deriva un `profile` mediante `AdaptivePersonalityAuthority.adapt(stable, AdaptivePersonalityRequest())` y lo incorpora al `system_prompt` mediante `replace(request, system_prompt=...)` (`preparation.py:83-107`). **El perfil permanece variable local en esta ruta examinada.**
2. `official_conversation_gateway.py:1464-1468`: lee opcionalmente `self._runtime.adaptive_personality_profile` para evidencia relacional. **La lectura no acredita un productor.**
3. `desktop_ui.py:212-219`: `_adaptive_delivery_tone` busca primero `adapter.adaptive_delivery_tone`; después busca `adapter.runtime._runtime.adaptive_personality_profile.delivery_tone` (verificar la forma exacta de acceso en el código). `desktop_ui.py:462-463,495-496,697-698` transmite el tono al lector de voz. **El lector no identifica el turno de procedencia.**
4. `voice_output.py:247-303,335-347`: admite `delivery_tone` opcional y aplica proyección expresiva acotada, conservando comportamiento neutral ante `None`/`NEUTRAL`.

**Hallazgo:** la proyección de M377 a inferencia es demostrable; la publicación productiva de ese mismo perfil hacia Gateway/Desktop/Voz **no está demostrada** por los elementos examinados.

## 3. Inventario de contratos protegidos

| Superficie | Evidencia concreta | Consecuencia |
|---|---|---|
| `core/runtime_composition_root/preparation.py` | `test_master_plan_canonical_personality_expression_projection_contract_red.py:33-116` | Mantener firma de proyección, campos de `LLMRequest`, `AdaptivePersonalityRequest()` sin enriquecimiento y ausencia de autoridades paralelas. |
| `app/official_conversation_gateway.py` | `test_r_mp_h4_voice_s2_canonical_adaptive_delivery_tone_productive_spoken_response_reachability_contract_red.py:49-58` | No insertar `adaptive_delivery_tone` en gateway; el test comprueba texto/firma pero su nombre no constituye una comprobación hash. |
| `app/runtime_ui_adapter.py` | Mismo test, líneas 61-66 | **SHA-256 fijado:** `2afb8629a78800c64932e289a905a098bb1a32bd5952ec152b204e42924a08e1`; cualquier cambio rompe el contrato. |
| `app/ui_adapter.py` / `UIResponse` | Mismo test, líneas 89-90 | Prohibido agregar `delivery_tone` a la firma de `UIResponse` sin reconciliación y autorización específicas. |
| `app/desktop_ui.py` | Mismo test, líneas 69-86 y 93-97 | Desktop debe consumir, no recalcular M377; fallback sin perfil continúa en `None`. |
| `app/voice_output.py` | `test_r_mp_h4_voice_s1_existing_adaptive_delivery_tone_to_vocal_expression_projection_contract_red.py` | Voz acepta una decisión de tono existente; no es autoridad para decidir personalidad. |

**Nota de precisión:** el test de gateway se titula `byte_identical_and_tone_neutral`, pero sus aserciones visibles no comparan SHA del gateway. No equiparar nombres de test con garantía criptográfica efectiva.

## 4. Riesgo de vida útil y concurrencia

El cálculo local del perfil dentro de `prepare()` se produce durante un turno, pero las lecturas del gateway y Desktop son atributos opcionales del runtime/adaptador. Si una futura implementación escribiera un atributo global mutable sin correlación por turno, podría mezclar perfiles entre turnos o sesiones. **No se ha demostrado que esa mezcla ocurra hoy:** no se ha demostrado tampoco la publicación del perfil real. Es un riesgo de diseño que un RED deberá cubrir antes de habilitar el transporte.

Un transporte aceptable debe preservar identidad de turno y sesión, duración acotada, ausencia de fuga entre respuestas simultáneas, no recomputación por Desktop/Voz y fallback neutral. La elección del mecanismo concreto **no queda autorizada por esta auditoría**.

## 5. Qué demuestran y qué no demuestran las pruebas existentes

- La proyección M55/M377 hacia `LLMRequest.system_prompt` está cubierta por seis contratos en `test_master_plan_canonical_personality_expression_projection_contract_red.py`.
- `test_r_mp_h4_voice_s2_canonical_adaptive_delivery_tone_productive_spoken_response_reachability_contract_red.py:14-40,69-86` construye un `_Runtime` sintético con `_Profile.delivery_tone = WARM`; comprueba consumo vocal y fallback sin perfil, **no** publicación desde el `profile` calculado en `GovernedRuntimePreparation.prepare`.
- El mismo archivo protege hash del adaptador, ausencia de `delivery_tone` en `UIResponse` y ausencia de recálculo de M377 en Desktop.
- No se acredita con esta auditoría una prueba end-to-end de composición real → mismo perfil M377 → misma respuesta → voz, ni un test de aislamiento concurrente de perfiles.
- El registro previo de 13.650 pruebas pasadas acredita la ejecución local comunicada por el Owner, no una ejecución nueva sobre este baseline.

## 6. Dictamen por condición

| Condición | Estado |
|---|---|
| Titularidad canónica M377 | EXISTING / VERIFIED STATIC |
| Proyección de M377 a inferencia | EXISTING / VERIFIED STATIC |
| Consumo opcional Gateway/Desktop/Voz | EXISTING / VERIFIED STATIC |
| Publicación de perfil productivo desde `prepare()` | UNVERIFIED |
| Asociación inequívoca perfil-respuesta-turno | UNVERIFIED |
| Aislamiento entre turnos/sesiones | UNVERIFIED |
| Hash del adaptador protegido | VERIFIED CONTRACT |
| Invariantes de Gateway, Desktop y `UIResponse` | VERIFIED CONTRACTS (alcance acotado) |
| RED ejecutable | HOLD |
| Certificación Owner | PENDING |
| `MODEL_ACQUISITION` | UNMAPPED / NO-GO |

## 7. Decisión y próximo paso

**RESIDUAL CANDIDATO, NO AUTORIZADO:** `M377_CANONICAL_TURN_PROFILE_TO_EXISTING_RUNTIME_VOICE_CONSUMER_PROVENANCE`.

Antes de RED: (a) revisar el objeto/resultado exacto de `prepare()` y el ciclo completo de composición→respuesta, (b) identificar cualquier canal por turno ya existente para metadatos expresivos, (c) revisar contratos de inmutabilidad adicionales del runtime/gateway/adaptador, (d) diseñar pruebas negativas de aislamiento y fallback sin modificar superficies protegidas, (e) solicitar aprobación Owner del residual y del seam exacto. Si aparece un canal canónico ya implementado, clasificar `NO RESIDUAL` en vez de duplicarlo.

**STOP:** sin cambios de código, tests, imports, dependencias o ZIP integral; sin autorización de adquisición, instalación ni ejecución neuronal.
