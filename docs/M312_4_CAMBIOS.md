# M312.4 — Composición controlada de memoria oficial

## Objetivo

Conectar explícitamente el BRAIN con el `OfficialMemoryGateway` real mediante
una fábrica aislada, sin incorporarlo al runtime visible de ROBY.

## Cambios

- Se agregó `OfficialMemoryBrainComposition`.
- Se agregó `build_official_memory_brain_composition(...)`.
- La composición construye:
  - `OfficialMemoryGateway` real;
  - `OfficialMemoryBrainAdapter` de solo lectura;
  - `AtomicJsonBrainRepository`;
  - `BrainService` con el adaptador como lector externo.
- Se agregaron pruebas de integración con `MemoryRuntimeIntegration` real.

## Límites deliberados

- No se modificó `main.py`.
- No se modificó `runtime_root_factory.py`.
- No se habilitaron escrituras desde el adaptador.
- No se migraron datos históricos.
- No se alteró el comportamiento visible de ROBY.
