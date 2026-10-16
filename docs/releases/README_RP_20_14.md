# ROBY XI.2 — RP.20.14

## Limpieza de módulos de forwarding

Esta revisión elimina reexports internos sin consumidores reales:

- `m5/__init__.py` deja de reenviar `ExecutionRegistry` y `EngineNotRegisteredError`.
- `m4/runtime/__init__.py` deja de reenviar `CognitiveRuntime`.
- La prueba interna del runtime importa desde `m4.runtime.runtime`, módulo propietario.

Las APIs canónicas permanecen disponibles en:

- `m5.registry`
- `m4.runtime.runtime`

Los demás `__init__.py` auditados se conservan porque funcionan como fachadas consumidas por runtime, composición o pruebas funcionales.

## Certificación de preparación

- `ruff check .`: limpio.
- `pytest -q`: 6562 passed.
