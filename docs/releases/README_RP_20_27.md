# RP.20.27 — Higiene del directorio raíz

Este overlay limita la raíz del repositorio a archivos de entrada, configuración y documentación principal.

## Cambios

- Las certificaciones históricas pasan a `docs/certifications/`.
- Las notas de overlays pasan a `docs/releases/`.
- Las auditorías generales pasan a `docs/reviews/`.
- Los documentos RP históricos pasan a `docs/refinement/`.
- Los aplicadores PowerShell pasan a `scripts/migrations/`.
- Se retiran copias exactas de documentos ya consolidados.
- Se retiran dos módulos de prueba duplicados en la raíz; sus versiones canónicas permanecen en `tests/`.
- Se eliminan cachés y bytecode regenerables.

## Deliberadamente preservado

- `main.py`, `pyproject.toml`, `README.md` y `CHANGELOG.md`.
- Ejemplos de configuración y dependencias opcionales.
- `.roby/` y `data/`, porque forman parte del estado operativo y su externalización requiere una política de rutas separada.
- Todo el código de producción y sus imports.
