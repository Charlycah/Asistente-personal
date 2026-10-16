# M306.2 — Limpieza conservadora de la raíz

La raíz del proyecto se redujo a archivos necesarios para ejecutar, instalar,
validar y orientar el proyecto:

- `main.py`
- `pyproject.toml`
- `requirements-audio-engine.txt`
- `requirements-voice.txt`
- `README.md`
- `CHANGELOG.md`

La documentación histórica no fue eliminada. Se trasladó a:

- `docs/history/root-notes/`
- `docs/history/manifests/`

No se movieron paquetes Python, scripts, pruebas, datos ni la configuración
persistente `.roby/`.
