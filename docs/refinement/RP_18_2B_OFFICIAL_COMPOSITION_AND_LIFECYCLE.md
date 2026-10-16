# RP.18.2B — Raíz oficial de composición y lifecycle unificado

## Objetivo

Establecer una única autoridad operativa que reúna el grafo oficial ya existente,
el bootstrap local, el lease/heartbeat, el supervisor y los servicios residentes.

## Decisión

`OfficialROBYRuntime` es la frontera única de lifecycle. No reemplaza los módulos
especializados: los coordina sin duplicar su construcción.

La cadena queda así:

`OfficialROBYRuntime -> OfficialRuntimeComposition -> conversation -> bootstrap -> root`

## Garantías

- `start()` y `stop()` son idempotentes.
- Los residentes arrancan después del lifecycle y del supervisor.
- Los residentes se detienen en orden inverso.
- Un fallo de arranque revierte lo que ya había arrancado.
- Escritorio conserva `DesktopPersonalRuntime` como fachada compatible.
- No se retira ni se fusiona todavía ningún composition root histórico.

## Fuera de alcance

El registro formal de salud y componentes residentes pertenece al Paso 4. El
snapshot operativo unificado pertenece al Paso 5.
