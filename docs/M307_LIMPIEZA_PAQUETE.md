# M307 — Limpieza del paquete

Cambios aplicados al ZIP de distribución:

- Eliminada la copia duplicada `.roby/models/vosk-es/vosk-model-small-es-0.42/`.
- Conservado el modelo canónico en `.roby/models/vosk-es/`.
- Retirado `.roby/credentials.json` con secretos reales.
- Agregado `.roby/credentials.example.json` sin secretos.
- Retiradas bases de datos, memoria, identidad, trazas y estado local de ejecución.
- Agregado `.gitignore` para evitar que estos datos vuelvan a empaquetarse.
- Agregado `.roby/README.md` con instrucciones de configuración segura.

Validación:

- `pytest -q`: 6970 passed.
- `python -m compileall -q .`: correcto antes de eliminar los artefactos generados.
- `ruff` no estaba instalado en el entorno de auditoría; debe ejecutarse localmente.
