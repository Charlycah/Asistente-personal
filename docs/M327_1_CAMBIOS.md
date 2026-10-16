# ROBY XI.2 M327.1 — First Autonomous Capability

## Objetivo

Incorporar la primera capacidad autónoma real y deliberadamente limitada de ROBY XI.2: verificar el estado actual de un componente degradado cuando el pipeline de autonomía controlada produce una autorización explícita.

## Implementación

Se añadió `core/controlled_autonomy/first_capability.py` con:

- `CapabilityRunStatus`
- `CapabilityRunResult`
- `ComponentHealthReader`
- `AutonomousCapabilityRunner`
- `VerifyComponentHealthCapability`
- `DeterministicFirstAutonomousCapabilityRunner`
- `default_first_autonomous_capability_runner()`

## Alcance

La única acción ejecutable es `verify_component_health`.

La capacidad consulta `ComponentHealthReader.get(component_id)` y transforma el resultado en un `DecisionOutcome`:

- `HEALTHY` -> `SUCCEEDED`
- `UNKNOWN` -> `UNKNOWN`
- cualquier otro estado -> `DEGRADED`
- error del adaptador -> `FAILED`

Luego envía el outcome al `OutcomeSupervisor`.

## Límites de seguridad

- Solo ejecuta con `DecisionDisposition.AUTHORIZE`.
- La decisión debe referenciar exactamente al candidato ejecutado.
- El candidato debe ser `verify_component_health`.
- El `component_id` debe provenir de la observación original.
- No reinicia componentes.
- No llama handlers de recuperación.
- No modifica contadores ni estados de salud.
- No ejecuta reintentos, reversiones, degradaciones ni notificaciones.

La composición por defecto usa un conjunto de candidatos deliberadamente estrecho para `runtime_component_degraded`, formado únicamente por la acción de verificación. Esto evita autorizar otra acción todavía no soportada por M327.1.

## Validación del entorno de construcción

```text
19 pruebas específicas OK
7669 pruebas totales OK
compileall OK
líneas <= 88 caracteres
```

Ruff debe validarse en el entorno local del proyecto.
