# ROBY XI.2 — ADAPTIVE PERSONALITY: M377/M390.5 CONTRACT PRECEDENCE & PRODUCTIVE CONSUMER RECONCILIATION

**Fecha:** 2026-10-10  
**Clase:** Auditoría documental y estática / PRE-RED  
**Baseline examinado:** `ROBY_XI_2_GOVERNED_MODEL_BACKEND_CANONICAL_AUTHORIZATION_TO_EXECUTION_SURGICAL_RECONCILIATION(1).zip`  
**Código modificado:** ninguno. **Tests ejecutados en esta auditoría:** ninguno. **Certificación Owner:** pendiente.

## 1. Orden de precedencia verificable

1. `docs/M377_ADAPTIVE_PERSONALITY.md` establece que `AdaptivePersonalityAuthority` es la única autoridad del perfil expresivo, que consume la identidad estable M55; señales explícitas normalizadas; sin persistencia, inferencia psicológica ni segundo cerebro.
2. `docs/M390_5_GOVERNED_EXPRESSIVE_MODULATION.md` define `GovernedExpressiveModulation` como adaptador puro subordinado, **no** autoridad alternativa. Su precedencia: `repairing` estable; sensibilidad explícita / `careful` estable; luego modulación simulada acotada a `neutral`, `warm`, `careful`; sin señal válida, M377 convencional; preferencias explícitas de detalle/estructura intactas.
3. `docs/ROBY_XI_2_MASTER_PLAN_CANONICAL_PERSONALITY_EXPRESSION_PROJECTION_CONTRACT_RED.md` delimita el **primer seam productivo**: M55 → M377 con `AdaptivePersonalityRequest()` sin señales enriquecidas → `LLMRequest.system_prompt`; prohíbe conectar inner state, Relationship Memory, Presence o inferencias ocultas en ese incremento.
4. `docs/ROBY_XI_2_MASTER_PLAN_CANONICAL_PERSONALITY_EXPRESSION_PROJECTION_SURGICAL_GREEN.md` registra ese seam como GREEN, con M55/M377 reutilizados y campos de solicitud preservados.
5. `docs/ROBY_XI_2_MASTER_PLAN_POST_PERSONALITY_PROJECTION_HUMANIZATION_HORIZON_RECONCILIATION.md` lo clasifica **CLOSED / OWNER-CERTIFIED**; reitera que señales enriquecidas exigen procedencia y residual separado. M390.5 existente no demuestra un productor ordinario de inner state ni autoriza conectarlo.

**Resolución:** M390.5 amplía la superficie contractual **admisible** de M377 bajo evidencia explícita, pero no revoca la restricción del primer seam ordinario. No hay contradicción: un contrato de capacidad más amplio no constituye autorización de integración productiva.

## 2. Evidencia de código

- `core/adaptive_personality.py:33-74`: `AdaptivePersonalityRequest` permite complejidad, urgencia, sensibilidad, preferencias y referencias afectivas; valida tonos permitidos y referencias de procedencia.
- `core/cognitive_maturity/governed_expressive_modulation.py:21-69`: adaptador `modulate()` genera un `AdaptivePersonalityRequest` preservando señales base y referencias; no construye perfil ni respuesta.
- `core/runtime_composition_root/preparation.py:394-407`: la preparación ordinaria evalúa M55, invoca M377 **con `AdaptivePersonalityRequest()`**, y proyecta el perfil en la solicitud de inferencia.
- `core/runtime_composition_root/preparation.py:84-107`: proyección expresiva acotada sobre `system_prompt` con tono, detalle y estructura; no evidencia de una asignación del perfil como atributo del runtime.

## 3. Consumidores

| Consumidor | Evidencia | Dictamen |
|---|---|---|
| Proveedor de inferencia ordinaria | `preparation.py:394-407` y proyección `:84-107` | **REACHABLE / PRODUCTIVE / DEFAULT SIGNALS ONLY** |
| Gateway de conversación, evidencia relacional | `app/official_conversation_gateway.py:1454-1492` obtiene `runtime.adaptive_personality_profile` con `getattr` | **LECTOR OPCIONAL; PRODUCTOR DE ESE ATRIBUTO NO DEMOSTRADO** |
| Desktop UI | `app/desktop_ui.py:212-219` lee tono del adaptador o perfil opcional del runtime | **LECTOR OPCIONAL; TONO EFECTIVO NO DEMOSTRADO** |
| Voz | El horizonte post-proyección documenta seam downstream capaz de consumir tono cuando está disponible | **CAPACIDAD DOCUMENTADA; CAUSALIDAD END-TO-END NO PROBADA AQUÍ** |
| M390.5 → preparación ordinaria | No aparece en `preparation.py:394-407` | **NO INTEGRADO EN ESTE SEAM, POR DISEÑO** |

La búsqueda textual en archivos Python de `app/` y `core/` del ZIP encontró `adaptive_personality_profile` solo en los dos lectores anteriores. Es una **ausencia de productor con ese nombre** en el alcance examinado, no una prueba de que todo transporte alternativo de tono sea inexistente.

## 4. Pruebas existentes y alcance

- `tests/test_m377_adaptive_personality.py`: contratos unitarios M377.
- `tests/test_m390_5_governed_expressive_modulation.py` y `tests/architecture/test_m390_5_governed_expressive_modulation_architecture.py`: contratos del adaptador subordinado.
- `tests/architecture/test_master_plan_canonical_personality_expression_projection_contract_red.py`: protege el primer seam con señales por defecto y proyección acotada.

El registro local aportado por el Owner indica **13.650 PASS y Ruff limpio**; no se ejecutó esa suite en esta auditoría y su éxito no prueba por sí mismo la disponibilidad del perfil para Gateway/UI/Voz.

## 5. Hallazgo de precedencia histórica adicional

El mismo ZIP contiene `docs/ROBY_XI_2_MASTER_PLAN_UNIFIED_EXPERIENCE_PROVIDER_RESPONSE_REACHABILITY_SURGICAL_GREEN.md`: documenta que el residual de presentación Unified Experience para respuestas del proveedor **ya fue cerrado mediante GREEN**. Por ello, no se debe reabrir ese residual basándose únicamente en un documento de horizonte anterior.

## 6. Clasificación y decisión

- `M55_TO_M377_ORDINARY_PROVIDER_PROJECTION`: **EXISTING / CLOSED**.
- `M390_5_PURE_ADAPTER`: **EXISTING / BOUNDED**.
- `M390_5_TO_ORDINARY_PROVIDER`: **NOT AUTHORIZED / PROVENANCE MISSING**.
- `RUNTIME_ADAPTIVE_PERSONALITY_PROFILE_ATTRIBUTE`: **OPTIONAL READERS FOUND / PRODUCER NOT PROVEN**.
- `DESKTOP_VOICE_EFFECTIVE_TONE`: **UNVERIFIED END-TO-END**.
- `NEW_PERSONALITY_AUTHORITY`: **DUPLICATE-RISK / FORBIDDEN**.
- `RED_AUTHORIZED`: **NO**.

## 7. Próximo paso único

`ADAPTIVE PERSONALITY — RUNTIME PROFILE/TONE PROPAGATION & VOICE CONSUMER CAUSAL TRACE — PRE-RED`

Seguir `LLMRequest` → resultado del pipeline → gateway → adaptador Desktop/Voz, comprobando rutas efectivas y consumidores de tono sin asumir que el perfil debe persistirse en el runtime. Si no hay brecha, declarar `NO RESIDUAL`. Si existe, definir un RED estrictamente acotado y someterlo al Owner. Mantener sin cambios el primer seam `AdaptivePersonalityRequest()` y no conectar M390.5 sin evidencia y autorización específica.

**STOP:** sin cambios de código, sin nuevos tests, sin RED/GREEN, sin adquisición neuronal, sin nueva autoridad.
