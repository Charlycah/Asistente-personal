# ROBY XI.2 — GATE 5.B.1
## Existing RuntimeCapabilityGraph + Official Runtime Provisioning → Read-Only Capability Dependency Reachability — SURGICAL RECONCILIATION

Status: SURGICAL RECONCILIATION — PENDING LOCAL CERTIFICATION  
Baseline de entrada: GATE 5.B certificado — 14,002 PASS + Ruff limpio + 0 FAIL.

## 1. Propósito
Resolver el residual estrecho G5-R3b sin modificar producción: determinar si el `RuntimeCapabilityGraph` existente ya está construido, poseído y provisionado por el runtime oficial de ROBY de forma canónica y, por tanto, si sus dependencias pueden alcanzarse read-only desde `UnifiedRuntimeObservability` sin crear otra autoridad, sin reconstruir el grafo y sin ejecutar análisis adicional.

Este Gate es únicamente inventario/reconciliación. No autoriza todavía CONTRACT RED ni SURGICAL GREEN productivo.

## 2. Autoridades existentes que se preservan
- `app.runtime_capability_graph.RuntimeCapabilityGraph`: grafo declarativo e inmutable de dependencias operacionales entre capacidades.
- `app.official_runtime_composition.OfficialROBYRuntime`: única autoridad de lifecycle/composición operacional oficial.
- `core.runtime_composition_root.RuntimeCompositionDependencies`: dependencias provisionadas por el runtime root.
- `app.unified_runtime_observability.UnifiedRuntimeObservability`: única proyección read-only unificada certificada para Analysis Mode.
- `app.runtime_health_readiness.RuntimeHealthReadinessService`: evaluación de readiness; no es propietario del grafo.
- `app.runtime_recovery_planner.RuntimeRecoveryPlanner`: consumidor del grafo para recovery; no es propietario del grafo.

No se crea ni se propone un segundo graph, registry, manager o observability runtime.

## 3. Hallazgo sobre RuntimeCapabilityGraph
`RuntimeCapabilityGraph` es una estructura real, madura y read-only en su semántica observable:

- valida unicidad de capabilities;
- valida referencias;
- rechaza ciclos;
- expone `snapshot()`;
- expone orden topológico mediante `ordered()`;
- expone dependientes directos/transitivos mediante `dependents()`;
- expone impacto por resident mediante `impacted_by_resident()`.

El grafo, por tanto, no necesita otra autoridad ni otro modelo para representar dependencias.

Sin embargo, la existencia de la clase no demuestra provisioning productivo.

## 4. Inventario de construcción/provisioning productivo
La búsqueda productiva no encuentra construcción de `RuntimeCapabilityGraph(...)` fuera de tests. En `app/`, `core/` e `infrastructure/` el tipo aparece únicamente como contrato/argumento consumido por:

- `UnifiedRuntimeObservability.snapshot(..., graph=None, ...)`;
- `OfficialROBYRuntime.observability(graph=None, ...)`;
- `OfficialROBYRuntime.readiness_graph(graph, ...)`;
- `OfficialROBYRuntime.recovery_plan(graph, ...)`;
- `RuntimeHealthReadinessService.evaluate_graph(...)`;
- `RuntimeRecoveryPlanner`.

No existe builder productivo, factory productiva ni wiring de environment que construya un graph oficial.

## 5. Inventario del runtime oficial
`OfficialRuntimeComposition` contiene únicamente `conversation`, `bootstrap`, `root`, `lifecycle` y `supervisor`.

`OfficialROBYRuntime.__init__()` crea servicios de snapshot/readiness/recovery/observability, pero no crea ni retiene un `RuntimeCapabilityGraph`.

`build_official_runtime_from_environment()` construye `OfficialRuntimeComposition` y devuelve `OfficialROBYRuntime(composition)` sin graph.

Por tanto:

**el runtime oficial no posee actualmente un `RuntimeCapabilityGraph` canónico provisionado.**

## 6. Inventario del RuntimeCompositionRoot
`RuntimeCompositionDependencies` sí provisiona `official_capability_registry`, pero no contiene ningún campo `runtime_capability_graph` / `capability_graph` equivalente.

`build_runtime_root()` construye y entrega el `OfficialRuntimeCapabilityRegistry` al root, pero no construye ni inyecta `RuntimeCapabilityGraph`.

Consecuencia: el capability registry oficial y el dependency graph son hoy artefactos distintos; no debe inferirse el graph desde el registry mediante scans o heurísticas.

## 7. UnifiedRuntimeObservability: alcanzabilidad actual
`UnifiedRuntimeObservability.snapshot()` acepta `graph` sólo como argumento opcional del caller.

Si `graph is not None`, usa ese objeto para solicitar un `RuntimeRecoveryPlan`. El snapshot unificado no publica el graph ni sus nodes/dependencies.

El flujo oficial de Analysis Mode invoca `UnifiedRuntimeObservability().snapshot(runtime)` sin suministrar graph. Por tanto, el nivel TECHNICAL no tiene actualmente dependency reachability oficial y no debe fingirla.

La semántica correcta de hoy sigue siendo `unavailable` / `not provisioned` para ese dato.

## 8. Matriz de reachability

| Pregunta | Evidencia real | Resultado Gate 5.B.1 |
|---|---|---|
| ¿Existe una autoridad/modelo de capability dependencies? | `RuntimeCapabilityGraph` | YES — EXISTING |
| ¿Es declarativo/read-only? | snapshot/order/dependents/impact; sin mutación pública del graph | YES |
| ¿Hay constructor productivo del graph? | ninguno encontrado fuera de tests | NO |
| ¿`OfficialROBYRuntime` lo posee? | no hay atributo/campo canónico | NO |
| ¿`OfficialRuntimeComposition` lo transporta? | no | NO |
| ¿`RuntimeCompositionDependencies` lo provisiona? | no | NO |
| ¿`build_runtime_root()` lo construye/injecta? | no | NO |
| ¿`build_official_runtime_from_environment()` lo construye/injecta? | no | NO |
| ¿`UnifiedRuntimeObservability` puede consumir uno externo? | sí, argumento opcional | YES — CALLER-SUPPLIED ONLY |
| ¿Unified observability publica dependencies? | no | NO |
| ¿Analysis Mode suministra graph? | no | NO |
| ¿Puede declararse dependency reachability oficial hoy? | no | NOT PROVISIONED |

## 9. Clasificación del residual G5-R3b
El residual queda refinado de `OPEN NARROW` a:

**EXISTING CANONICAL DECLARATIVE GRAPH TYPE + NO OFFICIAL PRODUCTIVE GRAPH INSTANCE / PROVISIONING + NO CERTIFIED READ-ONLY DEPENDENCY PROJECTION**

Esto es importante: el faltante no es “crear un graph”. El graph ya existe. El faltante real es decidir si ROBY debe tener una **instancia oficial declarativa** y quién puede construirla a partir de metadata explícita existente, sin inferirla del código y sin duplicar el capability registry.

## 10. Lo que este Gate NO autoriza
No se autoriza:

- añadir `RuntimeCapabilityGraph()` vacío sólo para satisfacer observability;
- derivar dependencias automáticamente desde imports, módulos, tests, registries o nombres;
- escanear `app/`, `core/`, `tests/` o documentación desde runtime;
- tratar `OfficialRuntimeCapabilityRegistry` como si ya expresara dependency edges;
- crear `CapabilityDependencyManager`, `DependencyRegistry`, `TechnicalInventoryManager` o segundo graph;
- ejecutar readiness/recovery sólo para poder mostrar un inventario;
- abrir episodes/budgets, versions, certifications o G5-R4.

## 11. Decisión arquitectónica
Gate 5.B.1 no puede cerrar G5-R3b sólo documentalmente, porque la instancia oficial del graph no existe/provisiona.

Pero tampoco corresponde saltar directamente a una implementación. Primero debe congelarse el contrato mínimo de una eventual instancia oficial:

1. una sola instancia declarativa y canónica;
2. construcción únicamente desde metadata explícita y gobernada, nunca por scans/inferencia;
3. ownership dentro del runtime oficial existente, no nueva autoridad;
4. publicación read-only del snapshot/dependency edges mediante `UnifiedRuntimeObservability`;
5. ausencia honesta cuando no exista configuración suficiente;
6. Analysis Mode sólo consume la proyección publicada;
7. no recovery/readiness side effects para observar dependencies.

## 12. Próximo Gate recomendado
Corresponde ahora una reconciliación contractual todavía más estrecha antes del RED:

**GATE 5.B.2 — Existing Official Capability Registry + Explicit Capability Dependency Metadata → Canonical RuntimeCapabilityGraph Provisioning Contract — CONTRACT BOUNDARY RECONCILIATION**

Objetivo: inventariar si las definiciones oficiales actuales de capabilities ya contienen metadata explícita suficiente para construir un único graph sin inferencia. Si no la contienen, el Gate debe declarar la ausencia y decidir el límite contractual, no inventar edges.

Sólo después de GATE 5.B.2 podrá decidirse si existe un CONTRACT RED legítimo.

## 13. Estado
- G5-R3a operational/errors/health/readiness/capabilities: CLOSED.
- G5-R3b capability dependencies: OPEN — provisioning contract unresolved.
- G5-R3c episodes/budgets: OPEN DEFERRED.
- G5-R3d versions: OPEN DEFERRED.
- G5-R3e certifications/quality: OUTSIDE CURRENT RUNTIME OBSERVABILITY.
- G5-R4 architectural evidence: DELIBERATELY OPEN / OUTSIDE THIS GATE.

## 14. STOP
No modificar producción en GATE 5.B.1. No crear CONTRACT RED todavía. No crear graph/manager/registry paralelo. No scans. No diagnostics automáticos. No ejecutar Reasoning, Planning, Reflection, Memory, Learning, recovery, Ruff o pytest desde Analysis Mode. No abrir G5-R4 ni los residuales deferred de G5-R3.
