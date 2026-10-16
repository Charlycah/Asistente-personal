# ROBY M255 — Ambient Context Runtime

## Objetivo

Conectar al runtime oficial la fundación de contexto ambiental M134 mediante una
fachada conversacional explícita, consentida y no autónoma.

## Capacidad oficial

`context.ambient_runtime`

## Operaciones

- `Registrá contexto ambiental: <observación>`
- `Declará contexto ambiental: <observación>`
- `Estado del contexto ambiental`

## Garantías

- No activa sensores.
- No realiza inferencias de presencia, actividad, acústica o espacio.
- No habilita automatización.
- No modifica el `.env`.
- Conserva el orden de las catorce capacidades anteriores.
- Reutiliza `AmbientContextFoundationEngine` y sus contratos existentes.

## Certificación

- Pruebas focalizadas: 93 passed.
- Ruff: All checks passed.
- Suite completa: 6094 passed.
- Skipped: 0.
- Regresiones observadas: 0.
