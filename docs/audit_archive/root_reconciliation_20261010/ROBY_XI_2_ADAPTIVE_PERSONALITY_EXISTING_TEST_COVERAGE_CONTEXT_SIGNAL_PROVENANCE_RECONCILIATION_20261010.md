# ROBY XI.2 — ADAPTIVE PERSONALITY — EXISTING TEST COVERAGE & CONTEXT SIGNAL PROVENANCE RECONCILIATION

**Fecha:** 2026-10-10  
**Estado:** Auditoría estática PRE-RED; certificación Owner pendiente.  
**Baseline inspeccionado:** `ROBY_XI_2_GOVERNED_MODEL_BACKEND_CANONICAL_AUTHORIZATION_TO_EXECUTION_SURGICAL_RECONCILIATION(1).zip`.  
**Alcance:** lectura de código y pruebas; sin modificaciones, sin ejecución de pytest en este incremento.

## 1. Contratos existentes — hallazgos verificables

| Evidencia | Resultado | Implicación |
|---|---|---|
| `core/adaptive_personality.py:34-44` | `AdaptivePersonalityRequest` ya admite `task_complexity`, `urgency`, `sensitive`, `requested_detail`, `requested_structure` y señales afectivas con procedencia | No ampliar el tipo ni crear otra autoridad sin necesidad |
| `tests/test_m377_adaptive_personality.py` | Ocho pruebas unitarias: validación, identidad estable, tono, sensibilidad, preferencias, complejidad/urgencia y límites de autoridad | Cobertura de la lógica de adaptación; no prueba alimentación contextual productiva |
| `core/runtime_composition_root/preparation.py:395-407` | El flujo ordinario invoca `adapt(stable, AdaptivePersonalityRequest())` y proyecta expresión al pedido de inferencia | La preparación ordinaria emplea valores por defecto |
| `tests/architecture/test_master_plan_canonical_personality_expression_projection_contract_red.py` | Seis pruebas: proyección acotada, preservación de solicitud, señales por defecto, exclusión de señales ricas, inyección canónica, no duplicación | El seam original está contractualmente restringido: modificarlo exige revisión del contrato |
| `core/cognitive_maturity/governed_expressive_modulation.py` | Adaptador puro `GovernedExpressiveModulation.modulate(...)` transforma estado interno y regulación en una solicitud M377 con referencias | Existe una vía canónica especializada; evitar un nuevo adaptador |
| `tests/test_m390_5_governed_expressive_modulation.py` | Seis pruebas para ausencia de estado, tono cálido/cuidadoso, preservación de detalle, prioridad estable y límites afectivos | Cobertura unitaria de procedencia y restricciones; no demuestra conexión a cada turno ordinario |
| `app/official_conversation_gateway.py:1466` y `app/desktop_ui.py:218` | Lectores de `adaptive_personality_profile` | No se encontró asignación productiva a ese atributo en la búsqueda de Python app/core del ZIP |

## 2. Procedencia y autoridad de las señales

- **Identidad y expresión estable:** `StablePersonalityEngine`; no se delegan identidad ni decisiones.
- **Adaptación expresiva:** `AdaptivePersonalityAuthority`; decide tono, detalle y estructura dentro de los límites de M377.
- **Señales de complejidad, urgencia, sensibilidad y preferencias:** campos admitidos por el contrato, pero la ruta ordinaria inspeccionada no acredita un productor autorizado que los inyecte en `AdaptivePersonalityRequest`.
- **Señal afectiva:** `GovernedExpressiveModulation` puede producir `affective_delivery_tone` a partir de `SimulatedInnerStateSnapshot`, preservando `snapshot_id` como referencia; la regulación puede agregar `report_id`. El contrato rechaza tonos afectivos fuera de `NEUTRAL/WARM/CAREFUL` y exige referencia de origen.
- **Gateway/UI/voz:** consumidores de tono o perfil existentes, pero no se acreditó equivalencia con el perfil de cada turno enviado al LLM. Los tests que definen perfiles sintéticos no prueban un productor productivo.

## 3. Contradicción aparente resuelta

La hipótesis anterior de “falta el productor de personalidad” queda descartada: el productor M377 y su proyección a `system_prompt` existen. La limitación real es distinta: **el seam productivo ordinario usa señales por defecto por diseño y por contrato**. El test `test_red_4_first_seam_does_not_infer_richer_humanization_signals` impide introducir directamente referencias a `GovernedExpressiveModulation`, `SimulatedInnerState`, `RelationshipMemory`, `SocialRegulation`, o parámetros de detalle, estructura y sensibilidad en `preparation.py`. Este límite debe interpretarse junto con el documento de alcance del incremento original y los hitos posteriores, antes de cambiarlo.

## 4. Cobertura que NO debe darse por demostrada

1. Un productor canónico de señales contextuales por turno, autorizado y con procedencia verificable, para la preparación ordinaria.
2. Una traza de integración que demuestre cómo llega `GovernedExpressiveModulation` a la ruta de inferencia ordinaria, si así lo exige el plan posterior.
3. Un snapshot por turno accesible en gateway/UI/voz y su consistencia con el `system_prompt` enviado.
4. Un test extremo a extremo que demuestre una respuesta real con variación contextual y ausencia de efectos sobre identidad, hechos y autorización.

Estos puntos son **UNVERIFIED/PARTIAL**, no fallos certificados. La búsqueda estática de símbolos no descarta productores indirectos, adapters o rutas de composición alternativas.

## 5. Decisión y secuencia de continuación

**DICTAMEN: PRE-RED — HOLD; RESIDUAL CANDIDATE, NOT CERTIFIED.**

1. Reconciliar la intención y vigencia del contrato de proyección `test_master_plan_canonical_personality_expression_projection_contract_red.py` con los hitos posteriores de M390.5 y de voz.
2. Trazar la autoridad de entrada para las señales explícitas (sin inferir afecto del usuario ni convertir simulaciones en hechos).
3. Comprobar consumidores indirectos y pruebas productivas antes de decidir si existe residual.
4. Solo si queda una brecha demostrada, presentar al Owner un RED quirúrgico que modifique **el contrato existente** bajo su autoridad, no que agregue un módulo paralelo.

**STOP:** no se modifica código ni pruebas; no se adquieren modelos; no se declara GREEN ni certificación Owner. La salida de 13.650 tests PASS corresponde al registro local aportado por el Owner, no a una ejecución nueva de esta auditoría.
