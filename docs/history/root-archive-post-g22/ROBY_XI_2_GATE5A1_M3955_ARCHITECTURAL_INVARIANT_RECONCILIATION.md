# ROBY XI.2 — GATE 5.A.1
## SURGICAL GREEN / M395.5 ARCHITECTURAL INVARIANT RECONCILIATION

**Tipo:** reconciliación quirúrgica dentro del mismo SURGICAL GREEN.  
**Motivo:** la primera ejecución integral del GREEN dejó un único fallo histórico en `tests/architecture/test_m395_5_orchestrator_synthesis.py::test_m395_5_gateway_initialization_uses_private_phases_only`.

## Hallazgo

El comportamiento de Analysis Mode cerró los ocho FAIL contractuales del RED, pero los value objects `AnalysisModeLevel`, `AnalysisModeStatus` y `AnalysisModeCommand` habían sido introducidos como clases top-level en `app/official_conversation_gateway.py`.

M395.5 protege una invariancia más antigua: ese archivo debe mantener exactamente tres clases top-level:

- `ConversationOrigin`
- `OfficialConversationGatewaySnapshot`
- `OfficialConversationGateway`

También protege la localización histórica del constructor `CanonicalCognitiveCore`.

## Reconciliación

No se modifica el test M395.5 ni se relaja su contrato.

Los tres value objects de Analysis Mode permanecen subordinados a `OfficialConversationGateway`, pero pasan a ser tipos anidados dentro de esa misma clase. No son manager, runtime, brain, registry ni autoridad nueva.

Con ello:

- las únicas clases top-level del archivo vuelven a ser las tres certificadas por M395.5;
- `CanonicalCognitiveCore(` permanece en la línea histórica protegida por M395.5;
- el estado `_analysis_mode_by_session`, los comandos explícitos, los tres niveles y la proyección sobre `UnifiedRuntimeObservability` permanecen funcionalmente iguales;
- `analizá X` continúa sin activar Modo Análisis;
- no se abre ninguna capacidad nueva.

## Alcance productivo

Se modifica únicamente `app/official_conversation_gateway.py` respecto del primer GREEN de GATE 5.A.1. No se añade módulo productivo nuevo.

## Validación focal del modelo

Los contratos focales de GATE 5.A.1, M395.5 y Unified Runtime Observability quedan verdes en el entorno del asistente.

La certificación integral sigue correspondiendo al entorno local del usuario con:

```text
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

## STOP

Sin cambios: no persistencia durable del modo, no preferencias aprendidas, no activación heurística, no diagnostics/scans automáticos, no Memory/Learning, no Planning N+1, no reparación, no background monitoring, no ampliación de autonomía y no chain-of-thought.
