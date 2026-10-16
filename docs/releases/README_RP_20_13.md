> **HISTORICAL / APPLIED / SUPERSEDED** — Este documento conserva la evidencia del refinamiento ya aplicado. El script asociado fue archivado en `docs/history/migrations/` y no forma parte del tooling operativo actual.

# ROBY XI.2 — RP.20.13

## Builders públicos de compatibilidad retirados

Esta revisión elimina cinco funciones de construcción triviales que habían quedado conservadas únicamente como compatibilidad después de RP.20.7:

- `build_official_conversation_gateway`
- `build_runtime_health_readiness`
- `build_runtime_operational_snapshot`
- `build_runtime_recovery_plan`
- `build_unified_runtime_observability_snapshot`

Las clases canónicas permanecen disponibles y son las utilizadas por el runtime oficial:

- `OfficialConversationGateway`
- `RuntimeHealthReadinessService`
- `RuntimeOperationalSnapshotBuilder`
- `RuntimeRecoveryPlanner`
- `UnifiedRuntimeObservability`

No se eliminan módulos físicos en esta revisión. La instalación por overlay es segura.

## Certificación del entorno de preparación

```text
ruff check .
All checks passed!

pytest -q
6558 passed
```

## Certificación local

Desde la raíz del proyecto:

```powershell
ruff check .
pytest -q
```

También puede ejecutarse:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\migrations\APPLY_RP_20_13.ps1
```
