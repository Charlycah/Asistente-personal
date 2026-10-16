# ROBY XI.2 — GATE 5.B.3.1
## Canonical RuntimeCapabilityGraph → UnifiedRuntimeObservability Read-Only Dependency Snapshot — SURGICAL GREEN

### Estado de entrada

- GATE 5.B.3.1 CONTRACT RED: certificado localmente por el usuario.
- Certificación RED: 14.019 PASS · 7 RED intencionales · Ruff limpio · sin fallos laterales.
- Fuente de verdad: ZIP CONTRACT RED corregido por Ruff.

### Cambio productivo mínimo

Se modifica exclusivamente `app/unified_runtime_observability.py` para cerrar la costura contractual ya congelada:

`OfficialROBYRuntime.capability_graph`
→ `RuntimeCapabilityGraph.snapshot()`
→ `UnifiedRuntimeObservabilitySnapshot.capability_dependencies`

El GREEN:

1. añade `capability_dependencies: tuple[RuntimeCapabilityNode, ...] | None` al snapshot unificado inmutable;
2. lee exclusivamente el atributo canónico `runtime.capability_graph`; por compatibilidad con lectores/stubs históricos sin ese atributo, su ausencia se interpreta como no provisionado (`None`), sin consultar ninguna autoridad alternativa;
3. conserva `None` cuando el grafo canónico no está provisionado;
4. conserva `()` cuando existe un `RuntimeCapabilityGraph(())` explícitamente provisionado;
5. publica exactamente `runtime.capability_graph.snapshot()` cuando existe grafo;
6. reutiliza los mismos `RuntimeCapabilityNode` canónicos inmutables;
7. no consulta `declared_capability_nodes()` ni reconstruye dependencias desde registry;
8. no construye otro `RuntimeCapabilityGraph`;
9. no usa `readiness_graph(...)` ni `recovery_plan(...)` para derivar la proyección;
10. mantiene el argumento histórico `graph=` exclusivamente en su función previa de recovery;
11. no modifica `OfficialConversationGateway` ni Analysis Mode.

### Superficie modificada

Producción:
- `app/unified_runtime_observability.py`

Documentación:
- este documento SURGICAL GREEN.

El CONTRACT RED y sus pruebas permanecen como contrato de regresión.

### STOP preservado

No se declaran dependencies productivas nuevas. No se modifica Analysis Mode. No se crea segundo graph/registry/manager/runtime. No se infieren dependencias. No se abren episodes/budgets, versions/certifications, G5-R4, Memory/Learning, Planning N+1 ni autonomía adicional.
