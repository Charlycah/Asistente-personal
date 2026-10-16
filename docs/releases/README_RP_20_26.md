# RP.20.26 — Retiro de reempaquetado de resultado compuesto

## Cambio

Se retiró `CognitiveCoreComponents.as_mapping()`. El método sólo reconstruía un
diccionario con los nueve campos públicos del resultado compuesto y no tenía
consumidores de producción.

Los campos de `CognitiveCoreComponents` son ahora la única superficie canónica.
No se retiraron proyecciones que ordenan, filtran, normalizan, aíslan estado o
tienen consumidores funcionales.

## Validación

- Ruff limpio.
- Pruebas focales verdes.
- Suite completa verde.
