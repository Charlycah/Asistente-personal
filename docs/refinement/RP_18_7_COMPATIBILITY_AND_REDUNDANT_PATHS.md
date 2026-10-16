# RP.18.7 — Compatibilidad y retiro de caminos redundantes

## Propósito

Clasificar las superficies históricas que siguen visibles, impedir que sean tratadas
como roots oficiales y retirar los bypasses operacionales detectados sin romper a
sus consumidores heredados.

## Decisiones

- `OfficialROBYRuntime` continúa como única autoridad operacional y de lifecycle.
- `build_desktop_app()` permanece como alias fino de
  `build_unified_desktop_app()`.
- `DesktopPersonalRuntime` se conserva para pruebas y consumidores históricos,
  pero el escritorio oficial ya no lo construye.
- `app.bootstrap:build_app` queda clasificado como composición histórica aislada,
  no ejecutable desde los entrypoints oficiales y bajo revisión para retiro.
- `build_operational_desktop_app()` permanece como adapter especializado sin
  lifecycle propio.

## Redundancias retiradas

El escritorio oficial antes envolvía lifecycle y supervisor ya pertenecientes a
`OfficialROBYRuntime` dentro de otra fachada. Ahora registra los residentes mediante
`official_runtime.with_residents(...)`, reutilizando la misma composición.

La captura visual ambiental antes accedía directamente al adapter interno de la
capacidad de cámara. Ahora construye una solicitud gobernada y llama a
`OfficialRuntimeCapabilityRegistry.execute_registration(...)` con origen
`ambient_proactive_runtime`.

## Registro de compatibilidad

`app/runtime_compatibility.py` documenta de forma ejecutable cada superficie como:

- canónica;
- alias fino;
- adapter especializado;
- legado aislado;
- retirado.

Ninguna superficie redundante queda marcada como root ejecutable.
