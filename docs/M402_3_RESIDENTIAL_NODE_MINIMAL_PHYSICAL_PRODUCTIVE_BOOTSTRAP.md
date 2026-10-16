# ROBY XI.2 — M402.3 Residential Node Minimal Physical/Productive Bootstrap

**Scope:** último hueco mínimo del Residential Node antes del cierre físico/productivo.

## Objetivo

Permitir que un host residencial real ejecute `ResidentRuntimeService` con identidad
M396 explícita y lease/heartbeat propios, sin arrancar `LocalRuntimeBootstrap` ni
componer un segundo `RuntimeCompositionRoot`.

## Implementación

- `ResidentLifecyclePort`: contrato neutral mínimo consumido por `ResidentRuntimeService`.
- `LongLivedRuntimeLifecycle` existente continúa siendo compatible para el runtime local.
- `ResidentialProcessLifecycle`: lifecycle de lease/heartbeat residencial sin cerebro.
- `ResidentialNodeProcessConfig`: configuración explícita de `ResidenceId`, componente,
  capabilities alojadas y paths operacionales.
- `ResidentialNodeProcessConfig.to_binding()`: deriva el `ResidentialNodeBinding` M402
  canónico sin duplicar identidad.
- `residential_node_process_entrypoint.py`: entrypoint físico mínimo que ejecuta el
  supervisor residencial con cero tareas por defecto y sin componer el root cognitivo.

## Invariantes M402.3

- RN-P01: el nodo residencial no compone `RuntimeCompositionRoot`.
- RN-P02: `ResidenceId` proviene exclusivamente de M396.
- RN-P03: M397 conserva autenticación/admisión/sesión/readiness.
- RN-P04: M398 conserva transporte físico.
- RN-P05: M402 integra/observa; no autoriza.
- RN-P06: `ResidentRuntimeService` no obtiene autoridad cognitiva.
- RN-P07: lease/heartbeat son metadata operacional, no memoria.
- RN-P08: pérdida del nodo no elimina autoridad del Primary Home.
- RN-P09: no existe replicación de memoria/knowledge/configuración.
- RN-P10: percepción residencial permanece fuera de alcance.

## Variables de entorno

- `ROBY_RESIDENCE_ID` — obligatoria.
- `ROBY_RESIDENT_COMPONENT_ID` — obligatoria.
- `ROBY_RESIDENT_CAPABILITIES` — lista opcional separada por comas.
- `ROBY_RESIDENT_HEARTBEAT_SECONDS` — default 30.
- `ROBY_RESIDENT_STALE_SECONDS` — default 120.
- `ROBY_RESIDENT_STATE_DIRECTORY` — default `.roby/residential_node`.

## No incluido

M402.3 no implementa Governed Synchronization, memory/knowledge replication,
Residential Perception, cámaras, sensores, ejecución cognitiva remota, un nuevo runtime,
una nueva authority ni un nuevo registry.

## Validación candidata

Baseline origen: M402.2 validada con 11.061 tests, Ruff limpio y M361 sincronizada.
M402.3 añade 11 tests; total esperado: **11.072 tests**.
