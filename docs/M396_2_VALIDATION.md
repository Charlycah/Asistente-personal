# M396.2 — Validación del incremento

## Resultado en este entorno

- Tests específicos M396.2: **28 passed**.
- Baseline M361 regenerada mediante `python scripts/generate_quality_baseline.py`.
- Test oficial de baseline M361: **5 passed**.
- Colección oficial Pytest M396.2: **10.358 tests**.
- Suite completa certificada en bloques disjuntos por archivos: **10.358 passed**.
- Un test de aceptación Gmail opt-in, fuera de la colección global normal, apareció
  adicionalmente como `skipped` al ejecutar su archivo de forma explícita.
- Compilación sintáctica de los archivos M396.2: correcta.
- `.roby` restaurado desde la baseline M396.1 después de las pruebas.
- `.roby/credentials.json`: checksum idéntico a M396.1.

## Ruff

Ruff no está instalado en el entorno de construcción disponible, por lo que no se
registra un resultado Ruff ficticio. La certificación final local debe ejecutar:

```powershell
ruff check .
python scripts/generate_quality_baseline.py
pytest -q
```

El resultado Pytest esperado para esta versión es **10.358 passed** (salvo cambios de
entorno en pruebas opt-in que no forman parte de la colección normal).
