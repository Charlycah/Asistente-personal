# RP.20.21 — Retiro de propiedad que exponía colaborador interno

## Cambio

Se retiró `OfficialConversationGateway.runtime`, una propiedad sin consumidores que
exponía directamente la instancia completa de `EndToEndLocalConversation`.

El gateway conserva únicamente vistas operativas explícitas (`bootstrap`, `history`,
`traces`, `snapshot`) y las operaciones gobernadas (`submit`, `converse`).

## Criterio arquitectónico

Una frontera no debe publicar su colaborador interno completo cuando no existe un
consumidor real ni una invariante asociada. Esto reduce acoplamiento y evita que nuevos
consumidores eludan la operación gobernada `submit()`.

## Validación

- `ruff check .`
- `pytest -q`
