# Limpieza estructural posterior a M186

La raíz fue reducida a los archivos operativos indispensables:

- `.env`
- `README.md`
- `config.example.json`
- `main.py`
- `pyproject.toml`

Se eliminaron manifiestos por hito, verificaciones transitorias, mensajes de commit, configuración local privada, cachés, bytecode y metadatos de herramientas.

La documentación histórica útil se conserva en `docs/history/milestones/`; las decisiones arquitectónicas permanecen en `docs/adr/`.

Validación posterior a la limpieza:

- 5142 pruebas pasando.
- Ruff limpio.
