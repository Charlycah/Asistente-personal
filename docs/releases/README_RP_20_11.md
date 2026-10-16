> **HISTORICAL / APPLIED / SUPERSEDED** — Este documento conserva la evidencia del refinamiento ya aplicado. El script asociado fue archivado en `docs/history/migrations/` y no forma parte del tooling operativo actual.

# ROBY XI.2 — RP.20.11

## Servicios directos y fronteras reales

Esta revisión elimina dos niveles ceremoniales:

- `ReasoningExplanationManager`, que sólo renombraba `ExplainableAnswerRenderer.render`.
- `ListPendingRemindersUseCase`, que ya no tenía consumidor operativo y sólo reenviaba `repository.list_pending`.

El orquestador de razonamiento recibe ahora directamente `ExplainableAnswerRenderer`.
La consulta de recordatorios pendientes usa directamente el puerto canónico `ReminderRepository`.

## Aplicación

Extraiga el ZIP sobre la raíz de ROBY y ejecute:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\migrations\APPLY_RP_20_11.ps1
```

El script comprueba que los símbolos obsoletos ya no estén presentes y ejecuta Ruff y toda la suite.

## Archivos físicos eliminados

Ninguno. Esta revisión elimina clases y exports dentro de módulos existentes, por lo que no requiere borrado de archivos por overlay.
