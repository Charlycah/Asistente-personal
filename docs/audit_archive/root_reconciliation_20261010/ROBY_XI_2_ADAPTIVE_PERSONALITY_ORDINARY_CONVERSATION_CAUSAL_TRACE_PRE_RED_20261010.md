# ROBY XI.2 — CANONICAL ADAPTIVE PERSONALITY PROFILE PRODUCTION → ORDINARY CONVERSATION CAUSAL TRACE — PRE-RED

**Estado:** PRE-RED documental; revisión de código estática; Owner certification pendiente.  
**Baseline:** `ROBY_XI_2_GOVERNED_MODEL_BACKEND_CANONICAL_AUTHORIZATION_TO_EXECUTION_SURGICAL_RECONCILIATION(1).zip`.  
**Alcance:** no cambios de código, pruebas, descargas ni autorización de modelos.

## 1. Precedencia contractual

`docs/M377_ADAPTIVE_PERSONALITY.md` establece: `StablePersonalityEngine` como productor del snapshot expresivo estable y `AdaptivePersonalityAuthority` como única autoridad del perfil adaptativo. M377 gobierna expresión (tono, detalle y estructura), no hechos, identidad, memoria, autorización o acciones. El documento de M377 declara que su hito original no incluía integración al runtime; el código de composición actual sí aporta esa integración posterior. La documentación posterior y el código deben reconciliarse antes de inferir una contradicción.

## 2. Traza causal observada

1. `app/runtime_root_factory.py:796-813` construye `StablePersonalityEngine()` y `AdaptivePersonalityAuthority()` y los inyecta en `RuntimeCompositionDependencies`.
2. `core/runtime_composition_root/models.py:139-140` declara ambas dependencias como opcionales.
3. `core/runtime_composition_root/preparation.py:395-407` evalúa la personalidad estable por turno, llama a `adaptive_personality.adapt(stable, AdaptivePersonalityRequest())` y enriquece `inference_request`.
4. `core/runtime_composition_root/preparation.py:84-107` construye un bloque `[CANONICAL STABLE PERSONALITY EXPRESSION]` con tono, detalle y estructura y lo añade a `LLMRequest.system_prompt` mediante `replace(...)`.
5. `app/official_conversation_gateway.py:1464-1492` intenta leer `runtime.adaptive_personality_profile` para evidencia relacional. En la búsqueda estática de archivos Python productivos del ZIP no se encontró una asignación a ese atributo. **Esto NO significa que el perfil no llegue a inferencia:** llega mediante `system_prompt` en la preparación.
6. `app/desktop_ui.py:212-219` intenta obtener `adaptive_delivery_tone` del adapter o el `delivery_tone` del perfil de runtime. Este canal no está demostrado como equivalente al perfil embebido en `system_prompt`.

## 3. Hallazgos clasificados

| ID | Hallazgo | Estado | Implicación |
|---|---|---|---|
| P01 | Productor canónico M377 y snapshot M55 conectados en preparación | EXISTING | No crear productor ni manager adicional |
| P02 | Proyección de tono, detalle y estructura a `LLMRequest.system_prompt` | EXISTING | Alcance hacia solicitud de inferencia demostrado por lectura estática |
| P03 | `AdaptivePersonalityRequest()` se construye sin señales específicas | PARTIAL / CANDIDATE | La personalización contextual de urgencia, complejidad, sensibilidad y preferencias no está demostrada en este camino |
| P04 | `adaptive_personality_profile` leído en gateway y UI, sin productor de atributo encontrado en archivos Python productivos | PARTIAL / VERIFY | La evidencia relacional y la voz podrían no consumir el perfil del turno; investigar otros mecanismos y límites de contrato |
| P05 | Efecto final en respuestas reales y cobertura end-to-end | UNVERIFIED | Requiere traza dinámica y pruebas existentes antes de proponer RED |
| P06 | Nueva autoridad de personalidad o cerebro paralelo | DUPLICATE-RISK | Prohibido |

## 4. Pruebas y documentación a contrastar antes de RED

- `tests/test_m377_adaptive_personality.py`: contratos unitarios de perfil, límites y determinismo.
- `tests/test_m40_cognitive_pipeline.py`: alcance del pipeline, sin asumir conexión productiva por su sola existencia.
- `tests/test_m24_desktop_ui.py`: observar cómo se consume tono.
- Pruebas de `runtime_composition_root` y `official_conversation_gateway`: buscar aserciones que prueben enriquecimiento real de `system_prompt` y conservación hasta proveedor/respuesta.
- `docs/M377_ADAPTIVE_PERSONALITY.md` y documentos posteriores de humanización: distinguir diseño original de integración posterior.

## 5. Decisión PRE-RED

**NO RED todavía.** La hipótesis original de ausencia de productor queda refutada por el código. Residual prioritario para validar: transporte de señales explícitas de contexto a la solicitud adaptativa canónica y, por separado, disponibilidad del perfil para evidencia relacional/UI/voz, si los contratos posteriores lo requieren. Primero verificar pruebas existentes, rutas alternativas, autoridad de señales y consumo de proveedor. Si se demuestra una brecha, proponer un único RED quirúrgico con aprobación del Owner.

**STOP:** sin código nuevo, sin autoridad nueva, sin inferencia/adquisición neuronal, sin GREEN, sin declarar certificación productiva.
