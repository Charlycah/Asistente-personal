# Legacy HAL Family Retirement — Validation Status

Baseline de partida: 14,191 PASS · 0 FAIL · Ruff clean.

Cirugía aplicada:
- retirada de `app/hal_config.py`;
- retirada de `core/hal.py`;
- retirada de `core/hal_console_application/`;
- retirada de `core/hal_voice_style_policy/`;
- retirada de `interfaces/cli/hal_console.py`;
- `legacy_hal_runtime` reclasificado como `RETIRED`;
- contratos M395.2/M395.4 sincronizados;
- migración `.hal/config.json` preservada en `app.roby_config`;
- Current Truth e inventario maestro sincronizados.

Validación ejecutada en el entorno de construcción:
- bootstrap/compatibility + M165/M172: 63 PASS · 0 FAIL;
- configuración/migración legacy: 21 PASS · 0 FAIL;
- `clean_project_caches.py`: PASS;
- `generate_quality_baseline.py`: PASS;
- full `pytest -q`: iniciado sin fallos, pero el runner local expiró aproximadamente al 1%;
- Ruff no está instalado en este entorno.

La certificación final debe ejecutarse en el entorno propietario con:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

No se agregaron ni eliminaron tests, por lo que el total esperado permanece en 14,191 PASS.


## Owner certification

Status: **CLOSED / CERTIFIED**.

Owner-environment result: **14,191 PASS · 0 FAIL · Ruff clean**.
