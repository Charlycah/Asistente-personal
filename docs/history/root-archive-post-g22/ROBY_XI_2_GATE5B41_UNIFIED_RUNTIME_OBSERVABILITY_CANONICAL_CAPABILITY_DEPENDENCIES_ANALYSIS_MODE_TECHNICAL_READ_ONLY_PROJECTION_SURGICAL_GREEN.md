# ROBY XI.2 — GATE 5.B.4.1 — SURGICAL GREEN

## Alcance

Cierra exclusivamente el CONTRACT RED certificado de GATE 5.B.4.1:

`UnifiedRuntimeObservabilitySnapshot.capability_dependencies`
→ `OfficialConversationGateway.analysis_mode_projection(...)`
→ nivel `TECHNICAL`.

## Cambio productivo mínimo

Único archivo productivo modificado:

- `app/official_conversation_gateway.py`

La proyección TECHNICAL:

- consume exclusivamente `snapshot.capability_dependencies`;
- publica `("capability_dependencies", snapshot.capability_dependencies)` cuando
  la proyección canónica está provisionada;
- representa `None` honestamente como
  `capability_dependencies: not provisioned`.

No lee `runtime.capability_graph` directamente.
No reconstruye dependencias desde registry.
No crea graph, manager, registry, runtime ni autoridad paralela.
No ejecuta readiness graph, recovery, diagnostics, reflection, reasoning,
planning, learning o memory para obtener la proyección.

## Autoridades preservadas

- `RuntimeCapabilityGraph`: autoridad canónica de dependencias.
- `OfficialROBYRuntime.capability_graph`: instancia canónica opcional.
- `UnifiedRuntimeObservability`: única superficie unificada read-only.
- `OfficialConversationGateway`: consumidor/presentador TECHNICAL, no autoridad.

## STOP preservado

Fuera de alcance:

- PERSONAL;
- ARCHITECTURAL / G5-R4;
- episodes / budgets;
- versions / certifications;
- Memory / Learning;
- Planning N+1;
- autonomía adicional.

## Validación

El GREEN debe cerrar únicamente los dos RED contractuales certificados y
mantener todas las protecciones del contrato.

La certificación final corresponde a la validación local:

1. `python scripts/generate_quality_baseline.py`
2. `ruff check .`
3. `pytest -q`
