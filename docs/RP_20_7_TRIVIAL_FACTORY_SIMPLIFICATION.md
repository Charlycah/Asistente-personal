# RP.20.7 — Simplificación de factories triviales

El runtime oficial dejó de atravesar builders que sólo construían objetos sin estado.

## Camino activo simplificado

`OfficialROBYRuntime` mantiene y reutiliza colaboradores explícitos para:

- snapshots operativos;
- readiness;
- planes de recuperación;
- observabilidad unificada.

La composición oficial construye `OfficialConversationGateway` directamente.

## Compatibilidad

Las funciones builder públicas permanecen disponibles para consumidores históricos, pero ya no forman parte del camino operativo principal.

## Invariantes

- el runtime oficial no importa ni llama builders triviales;
- los colaboradores sin estado se construyen una sola vez por runtime;
- los builders públicos históricos continúan disponibles.

## Certificación

- `ruff check .`: limpio;
- `pytest -q`: 6543 pruebas aprobadas.
