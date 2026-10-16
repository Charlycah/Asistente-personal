# RP.18.2C — Registro único de componentes residentes

## Objetivo

Reemplazar la colección anónima de residentes de `OfficialROBYRuntime` por un registro canónico que conserve identidad, criticidad, orden de inicio, estado, salud y último error de cada componente.

## Frontera incorporada

`app.resident_component_registry` define:

- `ResidentComponentRegistry`
- `ResidentRegistration`
- `ResidentCriticality`
- `ResidentState`
- `ResidentHealth`
- `registration_from_component`

## Garantías

- Identidades no vacías y no duplicadas.
- Orden determinista por `startup_order` e identidad.
- Estado observable: registered, starting, running, stopping, stopped y failed.
- Salud observable: unknown, healthy, degraded y unavailable.
- Fallos de residentes requeridos abortan y activan rollback.
- Fallos de residentes opcionales quedan registrados sin impedir el arranque global.
- Apagado en orden inverso.
- Compatibilidad con `OfficialROBYRuntime.residents`.
- Compatibilidad con residentes históricos: se registran como requeridos y conservan la semántica fail-fast.

## Alcance deliberadamente excluido

Esta entrega no crea todavía el snapshot operativo global ni unifica toda la observabilidad. El registro es la fuente estructurada que esas etapas consumirán.
