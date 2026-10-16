# ROBY XI.2 — GATE 5.B.3.1
## Canonical RuntimeCapabilityGraph → UnifiedRuntimeObservability Read-Only Dependency Snapshot — CONTRACT RED

### Estado de entrada

- GATE 5.B.3 — Existing Canonical RuntimeCapabilityGraph + UnifiedRuntimeObservability → Read-Only Capability Dependency Projection — CONTRACT BOUNDARY RECONCILIATION: CERTIFICADO Y CERRADO por el usuario.
- Baseline oficial declarada por el usuario: 14.016 PASS · Ruff limpio · 0 FAIL.
- Último GREEN productivo: GATE 5.B.2.1 — Official Capability Registration Explicit Dependency Declaration → Canonical RuntimeCapabilityGraph Provisioning — SURGICAL GREEN — CERTIFICADO Y CERRADO.
- M361 regenerado correctamente en la certificación local del usuario.

### Fuente de verdad y método

Este CONTRACT RED fue preparado sobre el ZIP de GATE 5.B.3 como fuente de verdad. El inventario se utilizó solamente como mapa de navegación y cada afirmación relevante fue verificada contra el código real de la baseline.

No se modifica producción en este Gate.

### Costura contractual congelada

La única costura autorizada es:

`OfficialROBYRuntime.capability_graph`
→ `RuntimeCapabilityGraph.snapshot()`
→ `UnifiedRuntimeObservabilitySnapshot.capability_dependencies`

El RED exige:

1. `UnifiedRuntimeObservabilitySnapshot` expone un campo subordinado read-only `capability_dependencies`.
2. `runtime.capability_graph is None` se proyecta como `None` y NO como `()`.
3. Un `RuntimeCapabilityGraph(())` deliberadamente provisionado se proyecta como `()` y NO como `None`.
4. La proyección es semánticamente idéntica a `runtime.capability_graph.snapshot()`.
5. Se preservan exactamente capability IDs, required dependency edges y optional dependency edges de los nodos canónicos.
6. Los nodos publicados son los mismos value objects canónicos inmutables; no se crea un modelo paralelo.
7. La proyección lee exclusivamente la instancia canónica `runtime.capability_graph`.
8. `OfficialRuntimeCapabilityRegistry.declared_capability_nodes()` NO se utiliza desde observability para reconstruir el graph.
9. El argumento histórico caller-supplied `graph=` puede seguir existiendo para recovery, pero NO puede gobernar ni sustituir la dependency projection canónica.
10. Producir la dependency projection no ejecuta `readiness_graph(...)` ni `recovery_plan(...)`.
11. La llamada ordinaria `runtime.readiness(...)`, ya integrante de la snapshot unificada, permanece fuera de esta costura y no se redefine en este Gate.
12. No se modifica `OfficialConversationGateway` ni Analysis Mode.
13. No se crea manager, registry, graph, runtime ni autoridad paralela.
14. No se infieren dependencias desde imports, wiring, nombres, metadata, tests, estructura o scans.

### RED esperado

La baseline de GATE 5.B.3 todavía no contiene `UnifiedRuntimeObservabilitySnapshot.capability_dependencies`. Por eso los contratos focales que requieren esa nueva superficie deben permanecer RED por una única causa arquitectónica: **la dependency snapshot canónica todavía no está publicada por UnifiedRuntimeObservability**.

Los contratos protectores de no reconstrucción, no Analysis Mode y preservación de `.roby/config.json` deben permanecer GREEN.

### Archivo contractual

`tests/architecture/test_gate5b31_canonical_runtime_capability_graph_unified_observability_dependency_snapshot_contract_red.py`

### STOP

No implementar GREEN automáticamente. No declarar nuevas dependencies productivas. No modificar `OfficialConversationGateway` / Analysis Mode. No crear segundo graph/registry/manager/runtime. No inferir dependencias. No abrir episodes/budgets. No abrir versions/certifications. No G5-R4. No Memory/Learning. No Planning N+1. No autonomía adicional.

La siguiente transición sólo queda autorizada después de certificación local del usuario con M361 + Ruff + pytest.
