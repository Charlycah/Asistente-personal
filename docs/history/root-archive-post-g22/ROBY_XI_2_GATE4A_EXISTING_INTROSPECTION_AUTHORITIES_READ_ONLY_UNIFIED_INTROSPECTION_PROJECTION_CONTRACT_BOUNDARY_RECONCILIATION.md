# ROBY XI.2 — GATE 4.A — Existing Introspection Authorities → Read-Only Unified Introspection Projection — Contract Boundary Reconciliation

## Tipo
Reconciliación contractual / inventario de seam. Sin cambios productivos.

## Baseline de entrada
GATE 4 — Introspection Reconciliation certificado por el usuario: **13.963 PASS + Ruff limpio + 0 FAIL**.

## Pregunta contractual
¿Puede ROBY exponer una vista introspectiva unificada, subordinada y read-only reutilizando las autoridades y superficies ya existentes, sin crear un nuevo cerebro, manager, registry, self-model, diagnostics engine o reflection authority?

## Hallazgo principal
Sí. El repositorio ya contiene una superficie que coincide materialmente con el seam buscado: `app.unified_runtime_observability.UnifiedRuntimeObservability`, expuesta oficialmente por `OfficialRuntime.observability(...)`.

Por tanto GATE 4.A **no debe crear un `UnifiedIntrospectionManager`, `AnalysisModeManager` ni una segunda proyección raíz**. La dirección correcta es extender, sólo si el contrato RED lo demuestra necesario, la observabilidad unificada existente con proyecciones introspectivas explícitas y read-only.

## 1. Proyección read-only existente

### Autoridad/superficie
`UnifiedRuntimeObservability` declara explícitamente: "Read canonical snapshots without owning or duplicating runtime state".

`UnifiedRuntimeObservabilitySnapshot` ya compone:
- estado operacional;
- readiness;
- estado de conversación;
- snapshot del gateway de capacidades;
- nombres de capacidades registradas;
- estado del cognitive core residente;
- recovery plan opcional.

### Reachability oficial
`OfficialRuntime` construye exactamente un `_observability_reader = UnifiedRuntimeObservability()` y expone `observability(...)`, que delega a esa misma superficie.

### Contratos existentes
`tests/test_rp_18_6_unified_observability.py` demuestra que:
- existe una única superficie oficial de observabilidad;
- lee estado real del gateway sin copiarlo;
- tolera ausencia del cognitive core;
- serializa a datos planos.

### Dictamen
**EXISTING / OFFICIAL / READ-ONLY / SUBORDINATE PROJECTION.** Éste es el seam canónico que GATE 4 debe reutilizar.

## 2. Capability Registry → proyección introspectiva

### Estado actual
`OfficialRuntimeCapabilityRegistry.interface_snapshot()` ya devuelve `RuntimeCapabilityView` inmutable con `name`, `description`, `enabled` y `tags`.

`UnifiedRuntimeObservability` actualmente expone `registered_capabilities` como nombres y el snapshot operacional del gateway, pero no incorpora todavía `interface_snapshot()` como vista rica.

### Frontera contractual recomendada
La introspección debe leer `interface_snapshot()` del registry existente. No debe:
- registrar/desregistrar capacidades;
- habilitar/deshabilitar capacidades;
- ejecutar interceptors;
- usar `execute_registration`;
- duplicar descriptores.

### Residual
**G4A-R1 — rich capability projection not yet included in unified observability.**

## 3. Self Model → proyección introspectiva

### Estado actual
El Self Model canónico está dentro de `CognitiveCoreRuntime`/`ContinuousInternalCognitiveLoop`. `ContinuousCognitiveState` ya contiene `self_model: CognitiveSelfModelSnapshot | None`.

`UnifiedRuntimeObservability._cognitive_snapshot()` recupera el snapshot del residente `cognitive_core_runtime`; por tanto la información del Self Model ya es alcanzable transitivamente cuando el residente está presente.

### Frontera contractual recomendada
La proyección unificada puede extraer/copiar únicamente el snapshot inmutable ya publicado. No debe llamar `CognitiveSelfModel.assess(...)`, iniciar ciclos ni mutar estado cognitivo.

Si el residente no está presente o aún no produjo estado, debe informar ausencia/no disponibilidad; nunca fabricar un Self Model.

### Residual
**G4A-R2 — self-model is transitively reachable but not an explicit introspection projection field.**

## 4. Reflection → proyección introspectiva

### Estado actual
`CanonicalReflectionFacade` ya define el mapa canónico de reflection y declara un único PRIMARY: `cognitive_core_resident`.

La facade expone un `snapshot` estructural seguro aunque no esté bound. El binding es necesario sólo para ejecutar `reflect(...)`.

`OfficialConversationGateway` construye una facade no bound; GATE 4 no debe resolver esto ejecutando reflexión desde introspección.

### Frontera contractual recomendada
La proyección introspectiva puede exponer:
- el snapshot canónico de componentes/roles;
- presencia del `cognitive_core_runtime` residente;
- estado publicado de reflexión ya contenido en el último `ContinuousCognitiveState`, si existe.

No debe:
- llamar `reflect(...)`;
- bindear silenciosamente la facade conversacional;
- iniciar reflexión;
- exponer chain-of-thought.

### Residual
**G4A-R3 — reflection architecture/state is available from existing sources but not yet projected explicitly by unified observability.**

El problema de binding identificado en GATE 4 deja de ser bloqueante para una proyección read-only: introspección no necesita ejecutar reflexión para describir el estado ya publicado.

## 5. Self Diagnostics → proyección introspectiva

### Estado actual
`GovernedSelfDiagnostics` es una autoridad técnica stateless con `AUTHORITY_ID = "self_diagnostics"`. Su método `diagnose(...)` requiere observaciones explícitas; no existe un "último diagnóstico" canónico que pueda leerse sin ejecutar una nueva evaluación.

No se encontró una instancia provisionada en `build_runtime_root()` ni una dependencia de `RuntimeCompositionDependencies` para self diagnostics.

### Frontera contractual recomendada
La proyección introspectiva **no debe ejecutar `diagnose(...)` para fabricar estado**. Hasta que exista un reporte/reader oficial durable o una instancia provisionada con evidencia explícita, la vista debe distinguir honestamente:
- autoridad implementada;
- runtime reachability no provisionada;
- diagnostic report actual no disponible.

Si un gate posterior necesita consultas diagnósticas productivas, deberá diseñar el seam de evidencia/reporte por separado, reutilizando `GovernedSelfDiagnostics`.

### Residual
**G4A-R4 — self-diagnostics authority exists, but no official current-report/read-only runtime source exists to project.**

Este residual no autoriza un nuevo diagnostics engine.

## 6. Seam canónico reconciliado

```text
OfficialRuntime
    └─ observability(...)
        └─ UnifiedRuntimeObservability       ← EXISTING projection seam
            ├─ OfficialRuntimeCapabilityRegistry.interface_snapshot()
            │      read-only
            ├─ cognitive_core_runtime.snapshot
            │      └─ state.self_model
            │      └─ state.reflection
            ├─ CanonicalReflectionFacade.snapshot
            │      structural declaration only
            └─ Self Diagnostics
                   authority exists
                   current report/runtime source = NOT YET AVAILABLE
```

## 7. Contrato mínimo recomendado para GATE 4.A.1 RED

El próximo RED debe exigir una **extensión de la superficie existente**, no una nueva autoridad.

Invariantes recomendados:
1. `UnifiedRuntimeObservability` sigue siendo la única superficie raíz de proyección/observabilidad.
2. `OfficialRuntime.observability(...)` sigue siendo la entrada oficial.
3. Capability projection usa exactamente `OfficialRuntimeCapabilityRegistry.interface_snapshot()`.
4. Capability projection es inmutable/read-only y no ejecuta capacidades.
5. Self Model projection se extrae sólo del snapshot publicado del `cognitive_core_runtime`.
6. Ausencia de cognitive core/self-model se representa como ausencia, no como estado inventado.
7. Reflection projection usa metadata de `CanonicalReflectionFacade.snapshot` y/o reflection ya publicada; no llama `reflect(...)`.
8. No se expone chain-of-thought ni razonamiento privado literal.
9. Self Diagnostics no ejecuta `diagnose(...)` durante observability.
10. Mientras no exista current-report source oficial, diagnostics se representa como `implemented but current report unavailable/not provisioned` o equivalente explícito.
11. No se crea `AnalysisModeManager`, `IntrospectionManager`, segundo registry, segundo self-model, segundo diagnostics engine ni segundo reflection authority.
12. No Memory/Learning writes, no Planning N+1, no execution, no repair, no code modification.
13. `.roby/config.json` permanece byte-identical.
14. `credencial.json`, si existe, se preserva.

## 8. Qué NO debe entrar en GATE 4.A.1

- parsing conversacional de "modo análisis";
- UI/panel de análisis;
- comandos para activar/desactivar capacidades;
- ejecución de diagnósticos nuevos;
- reparación automática;
- introspección background;
- persistencia nueva de Self Model;
- Memory/Learning;
- Planning;
- autonomía adicional;
- chain-of-thought.

## 9. Clasificación

**EXISTING OFFICIAL READ-ONLY PROJECTION SEAM + MINIMAL INTROSPECTION PROJECTION EXTENSION REQUIRED.**

La reconciliación reduce el residual de GATE 4: no falta una capa unificada desde cero; ya existe `UnifiedRuntimeObservability`. Falta enriquecer contractualmente esa proyección con datos introspectivos que las autoridades actuales ya publican, y representar con honestidad la ausencia de un current-report source de Self Diagnostics.

## STOP
GATE 4.A es documental/contractual. No autoriza cambios productivos.

## Siguiente gate
**GATE 4.A.1 — Existing UnifiedRuntimeObservability → Read-Only Introspection Projection Extension — CONTRACT RED.**
