# M334 — Persistencia del estado cognitivo

## Objetivo

Agregar persistencia JSON local y atómica para el contrato de estado cognitivo
introducido en M333.

## Archivos agregados

- `core/cognitive_state_contract/persistence.py`
- `tests/test_m334_cognitive_state_persistence.py`
- `M334_CAMBIOS.md`

## Archivos modificados

- `core/cognitive_state_contract/__init__.py`
- `CHANGELOG.md`

## Capacidad incorporada

- Contrato `CognitiveStateStore`.
- Implementación `JsonCognitiveStateStore`.
- Carga opcional cuando todavía no existe estado persistido.
- Escritura JSON atómica mediante archivo temporal y `os.replace`.
- Esquema versionado y validación estricta al cargar.
- Eliminación explícita del estado persistido.
- Ruta predeterminada local: `.roby/cognitive_state.json`.

## Límites deliberados

M334 no agrega actualización parcial, historial, inferencia, aprendizaje,
integración con el runtime ni escritura automática. La persistencia solo ocurre
cuando un consumidor invoca explícitamente `save`.
