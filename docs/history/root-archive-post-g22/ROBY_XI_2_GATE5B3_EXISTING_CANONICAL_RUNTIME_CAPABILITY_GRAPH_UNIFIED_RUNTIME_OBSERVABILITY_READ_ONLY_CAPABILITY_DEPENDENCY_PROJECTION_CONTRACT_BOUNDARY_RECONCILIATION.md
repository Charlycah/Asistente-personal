# ROBY XI.2 — GATE 5.B.3
## Existing Canonical RuntimeCapabilityGraph + UnifiedRuntimeObservability → Read-Only Capability Dependency Projection — CONTRACT BOUNDARY RECONCILIATION

### Baseline de entrada certificada
- GATE 5.B.2.1 — SURGICAL GREEN certificado por el usuario.
- Baseline oficial: **14,016 PASS + Ruff limpio + 0 FAIL**.

## 1. Propósito
Cerrar únicamente la reconciliación contractual entre el `RuntimeCapabilityGraph` canónico ya provisionable por `OfficialROBYRuntime` y la única superficie read-only de introspección certificada, `UnifiedRuntimeObservability`.

Este Gate no modifica producción y no introduce todavía CONTRACT RED. Su función es determinar la costura mínima y segura para publicar dependency reachability sin crear otra autoridad, sin reconstruir el grafo, sin inferir metadata, sin ejecutar readiness/recovery y sin abrir otros residuales técnicos o arquitectónicos.

## 2. Autoridades existentes que se preservan
- `app.runtime_capability_registry.OfficialRuntimeCapabilityRegistry`: source of truth de registrations y declaraciones explícitas.
- `app.runtime_capability_graph.RuntimeCapabilityGraph`: modelo canónico e inmutable de dependencias.
- `app.official_runtime_composition.OfficialROBYRuntime`: owner de la única instancia productiva opcional `capability_graph`.
- `app.unified_runtime_observability.UnifiedRuntimeObservability`: única superficie read-only unificada certificada.
- `app.official_conversation_gateway.OfficialConversationGateway`: consumidor conversacional; no debe convertirse en autoridad de dependencies.
- `RuntimeHealthReadinessService` y `RuntimeRecoveryPlanner`: consumidores operacionales del graph; no son fuentes de inventario.

No se propone un segundo graph, registry, manager, builder, observability runtime o technical inventory authority.

## 3. Estado real después de GATE 5.B.2.1
GATE 5.B.2.1 ya añadió una costura declarativa/provisioning gobernada:

1. `RuntimeCapabilityDependencyDeclaration` distingue metadata no declarada de declaración explícita.
2. `OfficialRuntimeCapabilityRegistry.declared_capability_nodes()` proyecta exclusivamente declaraciones explícitas a `RuntimeCapabilityNode`.
3. `build_official_runtime_from_environment()` construye `RuntimeCapabilityGraph(declared_nodes)` sólo cuando existen nodos explícitamente declarados.
4. `OfficialROBYRuntime` retiene esa instancia mediante la propiedad read-only `capability_graph`.
5. Si no existen declaraciones productivas explícitas, `capability_graph` permanece `None`.

La búsqueda actual confirma además que no existen todavía declaraciones productivas `RuntimeCapabilityDependencyDeclaration(...)` en `app/`, `core/` o `infrastructure/`. Por tanto, el runtime oficial construido hoy desde environment conserva honestamente `capability_graph=None`.

## 4. Estado real de UnifiedRuntimeObservability
`UnifiedRuntimeObservabilitySnapshot` publica actualmente:

- operational;
- readiness;
- conversation;
- capabilities;
- registered_capabilities;
- capability_registry;
- cognitive_core;
- self_model;
- reflection;
- self_diagnostics;
- recovery.

No existe un campo de dependency graph/dependency projection.

`UnifiedRuntimeObservability.snapshot(...)` conserva además un parámetro histórico opcional `graph`. Ese parámetro se usa exclusivamente para producir `runtime.recovery_plan(...)`; no publica el graph y no representa ownership canónico.

Por tanto, aunque `OfficialROBYRuntime.capability_graph` ya puede existir, la superficie unificada aún no lo lee ni lo publica.

## 5. Distinción contractual crítica: canonical graph vs caller-supplied graph
La futura proyección de dependencies debe leer **solamente** `runtime.capability_graph`.

No debe derivarse desde el argumento opcional `graph` de `UnifiedRuntimeObservability.snapshot(...)`, porque ese argumento:

- es caller-supplied;
- históricamente pertenece al cálculo de recovery;
- puede representar un objeto diferente de la instancia oficial;
- no prueba ownership/provisioning canónico.

Permitir que un caller suministre un graph alternativo como fuente de introspección violaría la regla de una sola autoridad/instancia canónica.

El parámetro histórico puede permanecer por compatibilidad para recovery, pero no debe gobernar la nueva dependency projection.

## 6. Semántica mínima de la proyección read-only
La costura correcta no necesita un nuevo modelo de dependencias. `RuntimeCapabilityGraph.snapshot()` ya devuelve los `RuntimeCapabilityNode` canónicos, inmutables y ordenados de forma determinista por capability id.

La futura proyección debe cumplir:

1. `runtime.capability_graph is None` → dependency projection explícitamente **NOT PROVISIONED**;
2. graph provisionado → publicar exclusivamente `runtime.capability_graph.snapshot()`;
3. no reconstruir nodes desde registry durante observability;
4. no consultar imports, wiring, nombres, tests, docs o filesystem;
5. no llamar `ordered()`, `dependents()` o `impacted_by_resident()` salvo que un contrato posterior demuestre que hace falta una vista derivada específica;
6. no llamar `readiness_graph(...)`;
7. no llamar `recovery_plan(...)` para obtener dependencies;
8. no ejecutar diagnostics, Reasoning, Planning, Reflection, Memory o Learning.

La forma más estrecha compatible con el snapshot actual es un campo read-only opcional, conceptualmente:

`capability_dependencies: tuple[RuntimeCapabilityNode, ...] | None`

`None` conserva **NOT PROVISIONED**. Una tupla proviene únicamente del snapshot del graph canónico ya retenido por el runtime.

## 7. Explicit-empty y NOT PROVISIONED no deben colapsarse
GATE 5.B.2.1 congeló `undeclared != explicit-empty` a nivel de registration.

En runtime oficial desde environment, el factory sólo construye graph cuando `declared_nodes` es no vacío. Por tanto, ausencia total de declaraciones sigue siendo `capability_graph=None`, no un graph vacío inventado.

La observabilidad debe preservar esa semántica: no convertir `None` en `()` para aparentar que ROBY conoce un graph vacío.

Si en tests o construcción explícita se inyecta deliberadamente un `RuntimeCapabilityGraph(())`, ese objeto representa un graph efectivamente provisionado por el caller de construcción del runtime; su snapshot vacío puede conservarse como empty-provisioned. No debe confundirse con `None`.

## 8. Analysis Mode: consumidor posterior, no parte del primer GREEN
El nivel TECHNICAL de Analysis Mode hoy consume `UnifiedRuntimeObservability` y no posee una fuente propia de dependencies.

La secuencia segura es:

1. certificar primero `OfficialROBYRuntime.capability_graph → UnifiedRuntimeObservability`;
2. después, en gate separado, decidir si `OfficialConversationGateway.analysis_mode_projection(...)` debe añadir una sección `capability_dependencies` cuando la snapshot unificada ya la publique.

No corresponde modificar Analysis Mode dentro del primer GREEN de esta costura. Esto evita mezclar fuente de verdad con presentación conversacional.

## 9. Matriz de reconciliación

| Pregunta | Estado real | Decisión GATE 5.B.3 |
|---|---|---|
| ¿Existe graph canónico? | Sí, tipo existente | PRESERVAR |
| ¿Puede existir una instancia oficial? | Sí, `OfficialROBYRuntime.capability_graph` | PRESERVAR |
| ¿Se construye sólo desde declarations explícitas? | Sí | PRESERVAR |
| ¿Hay declarations productivas actuales? | No encontradas | NO INVENTAR |
| ¿Observability publica dependencies? | No | RESIDUAL REAL |
| ¿Observability puede leer el runtime owner? | Sí, recibe `runtime` | COSTURA SUFICIENTE |
| ¿Debe usar caller-supplied `graph`? | No | PROHIBIDO COMO FUENTE CANÓNICA |
| ¿Hace falta nueva authority? | No | PROHIBIDO |
| ¿Hace falta readiness/recovery? | No | PROHIBIDO PARA PROYECCIÓN |
| ¿Debe Analysis Mode cambiar en el mismo GREEN? | No | DIFERIR |

## 10. Residual contractual aislado
El residual G5-R3b queda refinado a:

**CANONICAL RUNTIME GRAPH PROVISIONING CERTIFIED + UNIFIED OBSERVABILITY DOES NOT YET PUBLISH THE CANONICAL GRAPH SNAPSHOT — MINIMAL READ-ONLY PROJECTION SEAM REQUIRED**

El residual ya es suficientemente pequeño para CONTRACT RED.

## 11. Próximo Gate recomendado
Corresponde:

**GATE 5.B.3.1 — Canonical RuntimeCapabilityGraph → UnifiedRuntimeObservability Read-Only Dependency Snapshot — CONTRACT RED**

El RED debe exigir exclusivamente:

1. un campo subordinado en `UnifiedRuntimeObservabilitySnapshot` para dependency projection;
2. `None` cuando `runtime.capability_graph is None`;
3. identidad semántica exacta con `runtime.capability_graph.snapshot()` cuando existe;
4. ausencia de reconstrucción desde registry;
5. independencia respecto del argumento caller-supplied `graph` usado para recovery;
6. cero llamadas a readiness/recovery para producir la proyección;
7. serialización plain-data compatible mediante `as_dict()`;
8. preservación de `.roby/config.json` y de las autoridades existentes.

El CONTRACT RED no debe exigir todavía cambios en `OfficialConversationGateway` / Analysis Mode.

## 12. Cambios productivos
Ninguno.

Este Gate modifica únicamente documentación de reconciliación/estado y la baseline de calidad regenerada por el procedimiento habitual.

## 13. Estado de residuales
- G5-R3a operational/errors/health/readiness/capabilities: CLOSED.
- G5-R3b capability dependencies: **OPEN NARROW — observability projection seam isolated**.
- G5-R3c episodes/budgets: OPEN DEFERRED.
- G5-R3d versions: OPEN DEFERRED.
- G5-R3e certifications/quality: OUTSIDE CURRENT RUNTIME OBSERVABILITY.
- G5-R4 architectural evidence: DELIBERATELY OPEN / OUTSIDE THIS GATE.

## 14. STOP
No modificar producción en GATE 5.B.3. No crear CONTRACT RED dentro de este Gate. No declarar dependencies productivas. No reconstruir graph desde registry durante observability. No usar caller-supplied graph como fuente canónica. No ejecutar readiness/recovery para mostrar dependencies. No modificar Analysis Mode todavía. No crear manager/registry/graph paralelo. No abrir episodes/budgets, versions, certifications ni G5-R4. No activar diagnostics, Reasoning, Planning, Reflection, Memory, Learning, repair, background monitoring o autonomía.
