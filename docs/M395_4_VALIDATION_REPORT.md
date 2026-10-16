# M395.4 — Validation Report

## Base

M395.3 — Alineación Cognitiva, con los archivos corregidos proporcionados para
Ruff integrados antes de iniciar M395.4.

## Cambios

- Registro explícito de `core.hal:HAL` como `LEGACY_ISOLATED`.
- Registro explícito de `core.roby:ROBY` como `LEGACY_ISOLATED`.
- Inventario certificado de paquetes históricos M3–M7 con `frozen=True`.
- Política `modern_import_allowed=False` para M3–M7.
- Documentación reforzada del shim `m6.response.models`.
- 6 invariantes arquitectónicas nuevas para M395.4.

## Validación ejecutada en este entorno

- `compileall`: limpio.
- Tests focalizados de compatibilidad/legado: 48 passed.
- Tests de certificación de runtime: 19 passed.
- Colección completa: 10.324 tests.
- Suite completa ejecutada en 8 bloques disjuntos:
  - 1.291 passed
  - 1.291 passed
  - 1.291 passed
  - 1.291 passed
  - 1.290 passed
  - 1.290 passed
  - 1.290 passed
  - 1.290 passed
- Total: 10.324 passed, 0 failed.
- Baseline M361 regenerada.
- Estado `.roby` restaurado desde el handoff M395.3 antes de empaquetar.

## Pendiente de certificación local

Ruff no está instalado en el entorno de generación. Ejecutar en el entorno oficial:

```text
ruff check .
python scripts/generate_quality_baseline.py
pytest -q
```

Resultado esperado: Ruff limpio y 10.324 tests aprobados.

> **Post-Audit supersession note:** the HAL implementation family (`core.hal` and its HAL-specific config/console/voice surfaces) was later retired as a governed cleanup. This document remains historical evidence of the M395.4 certification state; `core.roby` and `m3→m7` remain preserved under their existing legacy contracts.
