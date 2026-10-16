# ROBY XI.2 — GATE 4 — Introspection Reconciliation

## Tipo
Reconciliación arquitectónica / inventario real. Sin cambios productivos.

## Baseline de entrada
GATE 3.C certificado por el usuario: 13.963 PASS + Ruff limpio + 0 FAIL.

## Objetivo
Reconciliar las autoridades ya existentes que pueden sostener una futura introspección gobernada antes de diseñar cualquier "Modo Análisis". Este gate no crea una nueva autoridad ni una nueva capacidad productiva.

## Regla rectora
Un solo ROBY, un solo cerebro gobernado, una autoridad canónica por capacidad. La introspección futura debe ser una superficie de lectura/composición sobre autoridades existentes; no un nuevo cerebro, planner, reasoner, diagnostics manager o reflection engine.

## 1. Capability Registry — estado real

### Autoridad existente
`app.runtime_capability_registry.OfficialRuntimeCapabilityRegistry` es la fuente ordenada de capacidades operacionales oficiales del runtime. Expone `registrations`, `capability_names`, `enabled_capability_names`, `registration_for(...)` e `interface_snapshot()`.

### Reachability
`app.runtime_root_factory.build_runtime_root()` crea una única instancia de `OfficialRuntimeCapabilityRegistry`, registra las capacidades productivas y la entrega al `RuntimeCompositionDependencies.official_capability_registry` y al interceptor operacional.

### Dictamen
**PRODUCTIVE / OFFICIAL / READABLE.** No crear un segundo Capability/Evolution Registry. El residual de GATE 4 es de proyección introspectiva: una futura vista puede consumir el registry existente, pero no poseerlo ni duplicarlo.

## 2. Self Model — estado real

### Autoridad/modelo existente
`app.cognitive_self_model.CognitiveSelfModel` y `CognitiveSelfModelSnapshot` modelan modo, foco, confianza, incertidumbre, carga, estabilidad, reevaluación, capacidades representadas, fuentes de evidencia, resumen y rationale.

### Reachability existente
El Self Model forma parte de `ContinuousInternalCognitiveLoop` y de `app.cognitive_core_runtime.CognitiveCoreRuntime`. El desktop bootstrap construye el continuous loop y lo registra como residente del personal runtime.

### Frontera demostrada
RP.18 declara explícitamente que Self Model no ejecuta capacidades, no altera agenda/hipótesis/world model/memoria, no solicita autorización y no almacena cadena privada de razonamiento.

### Residual real
El Self Model actual es **cognitivo y residente**, pero no constituye por sí solo una vista introspectiva integral del estado arquitectónico/productivo. No está demostrado que incorpore directamente el OfficialRuntimeCapabilityRegistry, certificaciones de calidad, estado M/CAP, self-diagnostics técnicos o el estado integral del runtime oficial.

### Dictamen
**OPERATIONAL / LIMITED SCOPE.** Reutilizar; no reemplazar ni expandirlo silenciosamente hasta convertirlo en un inventario arquitectónico.

## 3. Reflection — estado real

### Autoridad declarada
`app.canonical_reflection_facade` ya reconcilia múltiples componentes y declara exactamente un PRIMARY: `cognitive_core_resident` (`CognitiveCoreRuntime`). Los demás son collaborator/specialized/observer/legacy.

### Observación de reachability
`OfficialConversationGateway` crea un `CanonicalReflectionFacade`, pero en la construcción observada no queda demostrado un binding de esa facade al `CognitiveCoreRuntime`; sólo se observa binding explícito de cognitive state cuando está disponible. En paralelo, `runtime_root_factory` usa `OperationalCognitiveSource.reflection` como fuente consultiva determinística del runtime composition.

### Dictamen
**CANONICAL AUTHORITY DECLARED / PRODUCTIVE SURFACES PARTIALLY SPLIT.** Esto no justifica otra reflection authority. Antes de Modo Análisis debe aclararse qué superficie introspectiva lee la reflexión residente y cuál es sólo proyección consultiva del runtime.

## 4. Self Diagnostics — estado real

### Autoridad existente
`core.self_diagnostics.GovernedSelfDiagnostics` es la autoridad técnica única `self_diagnostics`.

### Cadena cerrada
M399.8 certifica la cadena gobernada:
Observación → tendencia → anomalía → hipótesis → confianza → evidencia → prueba reproducible → propuesta aislada → sandbox → tests → diff → explicación → decisión humana.

La cadena termina en decisión humana; no existe aplicación automática, reparación, rollback ni autopromoción.

### Reachability observada
La autoridad está consumida por contratos/tests y por la frontera subordinada de generación de propuestas (`app/self_improvement_proposal_generation.py`), pero no se encontró una instancia de `GovernedSelfDiagnostics` provisionada en `build_runtime_root()` ni una dependencia oficial de introspección que la exponga conversacionalmente.

### Dictamen
**SUBSTANTIAL / GOVERNED / NOT PROVEN AS OFFICIAL INTROSPECTION RUNTIME SURFACE.** No crear otro diagnostics engine. El residual es reachability/projection, no capacidad diagnóstica fundamental.

## 5. Mapa reconciliado

```text
OfficialRuntimeCapabilityRegistry
    └─ PRODUCTIVE / OFFICIAL / runtime-root reachable

CognitiveCoreRuntime
    ├─ canonical reflection resident
    └─ CognitiveSelfModel
         └─ OPERATIONAL / cognitive resident / limited introspection scope

GovernedSelfDiagnostics
    └─ SUBSTANTIAL / governed chain / human-controlled
       └─ not proven as official runtime introspection surface

Future Analysis Mode
    └─ MUST NOT become an authority
       └─ may only compose read-only projections from the authorities above
```

## 6. Residuales demostrados de GATE 4

### G4-R1 — Introspection projection contract absent
No se encontró una única superficie read-only que componga, sin adquirir autoridad, Capability Registry + Self Model + Self Diagnostics + certificación/runtime state.

### G4-R2 — Self Model scope is cognitive, not architectural
El Self Model existente no debe ser reinterpretado como inventario completo de ROBY. Se necesita preservar su contrato RP.18 y, si corresponde, proyectarlo como una fuente entre varias.

### G4-R3 — Self Diagnostics official runtime reachability not demonstrated
La capacidad diagnóstica existe y está cerrada, pero no se demostró una vía oficial de introspección/runtime para consultarla desde una futura superficie conversacional.

### G4-R4 — Reflection exposure/binding requires reconciliation
La autoridad primaria está declarada, pero la relación entre `CanonicalReflectionFacade`, `CognitiveCoreRuntime` residente y la fuente consultiva `OperationalCognitiveSource.reflection` debe quedar contractual antes de exponer reflexión como introspección.

## 7. Lo que NO falta

- No falta un Capability Registry nuevo.
- No falta un Self Model nuevo.
- No falta un Self Diagnostics engine nuevo.
- No falta otro Reflection Engine.
- No corresponde crear `AnalysisModeManager`, `IntrospectionManager`, `SelfAwarenessManager` ni otro cerebro.

## 8. Frontera recomendada para el siguiente gate

**GATE 4.A — Existing Introspection Authorities → Read-Only Unified Introspection Projection — CONTRACT BOUNDARY RECONCILIATION**

Pregunta contractual central:

> ¿Puede una superficie subordinada y read-only componer snapshots de las autoridades existentes —sin mutarlas, sin ejecutar capacidades y sin inventar estado— y quedar disponible por el runtime oficial como base futura de Modo Análisis?

Primero reconciliar el contrato. Sólo si se demuestra un seam mínimo: CONTRACT RED → certificación RED → SURGICAL GREEN.

## STOP

GATE 4 no autoriza:
- Modo Análisis productivo todavía;
- nueva autoridad cognitiva;
- segundo registry/self-model/diagnostics/reflection engine;
- Memory o Learning writes;
- Planning N+1;
- ejecución de capacidades desde introspección;
- reparación automática;
- modificación automática de código;
- exposición de chain-of-thought/pensamiento secreto;
- estados emocionales/subjetivos inventados;
- background monitoring nuevo;
- modificación de `.roby/config.json`.

Preservar `credencial.json` si está presente.

## Dictamen

**GATE 4 — INTROSPECTION RECONCILIATION — COMPLETE.**

Clasificación global:

**EXISTING SUBSTANTIAL AUTHORITIES + MINIMAL READ-ONLY INTROSPECTION PROJECTION / OFFICIAL REACHABILITY SEAM REQUIRED.**

No se justifica implementar Modo Análisis directamente. El siguiente paso correcto es GATE 4.A contractual.
