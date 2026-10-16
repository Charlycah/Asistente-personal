# M396.3 — Validation

## Validación disponible en el entorno de construcción

- Tests nuevos de Authority Preservation: 12/12 aprobados.
- Test oficial de reproducibilidad M361: 5/5 aprobado.
- Colección oficial Pytest: 10.370 tests.
- Manifiesto de nueve fronteras críticas: SHA-256 verificado sin cambios.
- `core.residence_domain`: sintaxis Python verificada.
- `.roby` restaurado desde la baseline M396.2 después de las pruebas; credenciales sin cambios.

## Certificación local requerida

El entorno de construcción no dispone de Ruff y la suite histórica completa no logra
finalizar dentro de los límites de ejecución disponibles. La certificación oficial de
M396.3 requiere en la máquina de desarrollo:

```powershell
ruff check .
python scripts/generate_quality_baseline.py
pytest -q
```

Resultado Pytest esperado: **10.370 passed**.
