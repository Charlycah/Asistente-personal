# ROBY XI.2 — M377 Runtime Profile Projection: Canonical Owner & Protected-Seam RED Readiness

**Fecha:** 2026-10-10  
**Tipo:** reconciliación estática PRE-RED / READINESS  
**Baseline:** `ROBY_XI_2_GOVERNED_MODEL_BACKEND_CANONICAL_AUTHORIZATION_TO_EXECUTION_SURGICAL_RECONCILIATION(1).zip`  
**Estado:** propuesta de auditoría, **sin certificación Owner**, sin cambios al baseline.

## 1. Alcance y método

Inspección directa de archivos dentro del ZIP, cotejando la traza PRE-RED anterior con las fuentes de composición, preparación, gateway, Desktop y pruebas contractuales. No se ejecutó la aplicación ni la suite completa. No se interpreta la ausencia de coincidencias textuales como prueba absoluta de ausencia de rutas dinámicas.

## 2. Titularidad canónica demostrada

| Objeto / decisión | Propietario demostrado | Evidencia | Límite |
|---|---|---|---|
| Autoridad de personalidad estable M55 | `StablePersonalityEngine` | `app/runtime_root_factory.py:796`; `core/runtime_composition_root/preparation.py:398` | No sustituible |
| Autoridad adaptativa M377 | `AdaptivePersonalityAuthority` | `app/runtime_root_factory.py:797,812-813`; `preparation.py:399-402` | No sustituible |
| Perfil calculado para el turno | Variable local `profile` en `GovernedRuntimePreparation.prepare` | `preparation.py:395-407` | Su titularidad de publicación posterior **no está demostrada** |
| Proyección a inferencia | `GovernedRuntimePreparation._enrich_with_canonical_personality_expression` | `preparation.py:83-107,403-407` | Modifica únicamente `system_prompt` por `replace` |
| Consumidor Desktop/voz | `_adaptive_delivery_tone` y `voice_reader.read` | `app/desktop_ui.py:212-219` y traza PRE-RED anterior | Lector opcional; no productor |
| Consumidor gateway | Lectura opcional de `self._runtime.adaptive_personality_profile` | `app/official_conversation_gateway.py:1464-1468` | No prueba publicación |

**Conclusión de ownership:** la **decisión M377** pertenece a la autoridad adaptativa existente, y el perfil por turno se obtiene en la preparación canónica. No está demostrado que `RuntimeCompositionRoot` conserve o publique ese perfil como atributo de runtime. La publicación y su ciclo de vida por turno son el punto por resolver, no una nueva autoridad de personalidad.

## 3. Seam protegido y precedencia

La prueba existente `tests/architecture/test_master_plan_canonical_personality_expression_projection_contract_red.py` establece:

- `test_red_1`: firma acotada de la proyección (`request`, `stable`, `profile`).
- `test_red_2`: preservación de los demás campos de `LLMRequest` y adición expresiva al `system_prompt`.
- `test_red_3`: `AdaptivePersonalityRequest()` **sin señales enriquecidas**.
- `test_red_4`: exclusión explícita de `GovernedExpressiveModulation`, `SimulatedInnerState`, `RelationshipMemory`, `SocialRegulation` y señales de detalle, estructura, tono afectivo o sensibilidad en `preparation.py`.
- `test_red_5`: composición centralizada de dependencias en `runtime_root_factory.py`.
- `test_contract_no_parallel_personality_or_humanization_runtime_is_created`: prohíbe rutas paralelas conocidas.

Por ello **no está autorizado** añadir M390.5 ni señales nuevas al seam ordinario, reescribir `LLMRequest`, mutar `UIResponse` o crear un segundo adaptador. Antes de cualquier cambio deben inspeccionarse además las pruebas de invariantes/hash aplicables a `official_conversation_gateway.py`, `runtime_ui_adapter.py` y la proyección Desktop→voz; la presente revisión no certifica su exhaustividad.

## 4. Cadena causal y brecha residual

`runtime_root_factory.py` construye las autoridades → `preparation.py` calcula `profile` → lo incorpora a `LLMRequest.system_prompt` → la ruta de voz busca opcionalmente `adapter.adaptive_delivery_tone` o `runtime.adaptive_personality_profile.delivery_tone`.

**No hay una relación de datos demostrada** entre la variable local `profile` y esos atributos de lectura. El contrato de voz previamente identificado usa un runtime sintético con perfil inyectado: prueba el consumidor, no el productor productivo.

**Residual candidato:** `M377_CANONICAL_TURN_PROFILE_TO_EXISTING_RUNTIME_VOICE_CONSUMER_PROVENANCE`.

**Riesgo arquitectónico adicional a resolver antes de RED:** publicar un perfil mutable global de runtime podría mezclar tonos de turnos concurrentes o sucesivos. La futura proyección, si se autoriza, debe demostrar identidad del turno, vida útil acotada, ausencia de filtración entre usuarios y conservación de fallback neutral.

## 5. Readiness contractual

| Condición | Dictamen |
|---|---|
| Identidad de autoridad M377 y su punto de cálculo | **PASS — estático** |
| Proyección M377 a inferencia | **PASS — estático** |
| Consumidor Desktop/voz | **PASS — estático** |
| Productor runtime→voz con perfil real | **UNVERIFIED** |
| Canal por turno, identidad y concurrencia | **UNVERIFIED** |
| Inventario completo de seams protegidos y hashes | **UNVERIFIED** |
| Reutilización sin autoridad paralela | **MANDATORY** |
| Aprobación Owner del residual | **PENDING** |
| RED ejecutable | **HOLD** |

## 6. Contratos RED mínimos propuestos, no implementados

1. La composición real calcula un único perfil M377 para el turno y preserva su procedencia.
2. Si se publica hacia un consumidor, el perfil pertenece al **mismo turno** y no se reconstruye en Desktop.
3. Dos turnos distintos, incluyendo ejecución concurrente, no comparten accidentalmente el perfil ni su tono.
4. Ausencia de perfil conserva el fallback vocal existente.
5. `LLMRequest`, `UIResponse`, gateway y adaptador conservan sus invariantes protegidas.
6. M390.5 no ingresa al seam ordinario por esta modificación.
7. El test de alcance productivo usa composición y consumidores reales, no solamente inyección sintética.

Estas pruebas son un **diseño de cobertura**; no se agregaron al repositorio ni se ejecutaron.

## 7. Decisión y próxima intervención permitida

**READINESS: CONDITIONAL HOLD.** La autoridad que calcula M377 está identificada; **no está certificado el canal permitido de publicación del perfil hacia voz**, ni el inventario completo de contratos protegidos. Próximo paso: auditoría enfocada del ciclo de vida del turno y de los contratos de gateway/adaptador/voz, seguida de aprobación Owner del residual exacto. Solo entonces RED contractual quirúrgico.

`MODEL_ACQUISITION` permanece **UNMAPPED / NO-GO**. No se modificaron código, pruebas, dependencias, imports ni baseline.
