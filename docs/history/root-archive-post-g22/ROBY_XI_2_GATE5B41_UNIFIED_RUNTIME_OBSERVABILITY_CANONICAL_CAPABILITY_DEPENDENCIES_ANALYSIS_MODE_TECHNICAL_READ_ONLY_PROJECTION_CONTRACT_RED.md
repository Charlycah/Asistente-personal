# ROBY XI.2 — GATE 5.B.4.1 — CONTRACT RED

## UnifiedRuntimeObservability Canonical Capability Dependencies → Analysis Mode TECHNICAL Read-Only Projection

### Estado de entrada certificado

- GATE 5.B.3.1 SURGICAL GREEN: CERTIFICADO Y CERRADO.
- GATE 5.B.4 ARCHITECTURAL RECONCILIATION: CERTIFICADO Y CERRADO.
- Baseline local certificada: **14.026 PASS, Ruff limpio, 0 FAIL**.
- `UnifiedRuntimeObservabilitySnapshot.capability_dependencies` ya es una proyección canónica read-only de `OfficialROBYRuntime.capability_graph`.
- Analysis Mode ya existe bajo `OfficialConversationGateway`; no se crea otra autoridad.

## Objeto contractual

Congelar exclusivamente el residual demostrado por GATE 5.B.4:

`runtime.capability_graph`
→ `UnifiedRuntimeObservabilitySnapshot.capability_dependencies`
→ Analysis Mode `TECHNICAL`

El gate NO vuelve a resolver dependencias. Sólo permite que la proyección TECHNICAL seleccione y presente el valor que ya publica `UnifiedRuntimeObservability`.

## Contratos RED

1. La rama TECHNICAL debe seleccionar explícitamente `snapshot.capability_dependencies`.
2. Si `capability_dependencies is None`, TECHNICAL debe representarlo honestamente como **not provisioned**; `None` no puede convertirse en `()`.
3. Si existe una proyección, TECHNICAL debe entregar el objeto read-only recibido de `UnifiedRuntimeObservability`, sin reconstruir nodos/aristas.
4. La proyección no puede leer `runtime.capability_graph` directamente: su única fuente para esta información es el snapshot unificado.
5. No puede consultar `OfficialRuntimeCapabilityRegistry`, `declared_capability_nodes()` ni construir `RuntimeCapabilityGraph` para esta presentación.
6. No puede ejecutar `readiness_graph()`, `recovery_plan()`, diagnostics, reflection, reasoning, planning, Memory o Learning para obtener dependencias.
7. PERSONAL queda fuera de alcance.
8. ARCHITECTURAL/G5-R4 queda fuera de alcance.
9. Episodes/budgets quedan fuera de alcance.
10. Versions/certifications quedan fuera de alcance.
11. No se crea manager, registry, graph, runtime ni autoridad introspectiva paralela.
12. `.roby/config.json` permanece byte-identical.
13. `UnifiedRuntimeObservability` permanece sin cambios: este gate consume una fuente ya certificada, no la redefine.

## RED esperado

La única causa arquitectónica del RED debe ser que la rama TECHNICAL de `OfficialConversationGateway.analysis_mode_projection()` todavía no selecciona ni representa `capability_dependencies`.

No se autoriza GREEN automático.

## STOP

STOP antes de:
- PERSONAL;
- ARCHITECTURAL / G5-R4;
- episodes / budgets;
- versions / certifications;
- nuevas declaraciones productivas de dependencias;
- Memory / Learning;
- Planning N+1;
- autonomía adicional.

Metodología: reconciliación → CONTRACT RED → validación local M361 + Ruff + pytest → autorización explícita → SURGICAL GREEN.
