# M395.4 — Compatibilidad y Legado

## Objetivo

Cerrar la relación entre el runtime moderno de ROBY XI.2 y la arquitectura histórica
M3–M7 sin borrar comportamiento histórico ni crear nuevas autoridades.

## Decisiones

- `core.hal:HAL` y `core.roby:ROBY` quedan registrados como
  `LEGACY_ISOLATED` en `app.runtime_compatibility`.
- Ninguno de los dos puede ser considerado root oficial de ejecución.
- Los paquetes `m3`, `m4`, `m5`, `m6` y `m7` quedan formalmente congelados.
- Las capas modernas no pueden incorporar nuevos imports hacia M3–M7.
- `m6.response.models` permanece únicamente como shim de compatibilidad hacia
  `domain.response`, preservando identidad de tipos.
- No se elimina código histórico en M395.4.

## Invariante

Una superficie histórica reemplazada por una autoridad canónica puede existir por
compatibilidad, pruebas o evidencia, pero no puede adquirir nuevas capacidades,
nuevas decisiones ni convertirse nuevamente en ruta oficial de ejecución.

## Resultado

El runtime moderno ya no depende de M3–M7. Las únicas dependencias productivas
modernas detectadas hacia esos paquetes están confinadas a `core.hal` y
`core.roby`, explícitamente clasificados como históricos.

> **Post-Audit supersession note:** the HAL implementation family (`core.hal` and its HAL-specific config/console/voice surfaces) was later retired as a governed cleanup. This document remains historical evidence of the M395.4 certification state; `core.roby` and `m3→m7` remain preserved under their existing legacy contracts.
