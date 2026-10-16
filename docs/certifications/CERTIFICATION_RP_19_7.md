# Certificación RP.19.7

## Hito

Aprendizaje adaptativo de prioridades y costos.

## Resultado

- Ajustes adaptativos persistentes sin modificar estimaciones autoritativas.
- Aprendizaje por progreso, estancamiento y revisión metacognitiva.
- Límites de política, rationale trazable y reinicio explícito.
- Integración con la cola deliberativa existente.
- Sin modelos externos ni sistemas paralelos.
- Migración SQLite compatible con RP.19.1–RP.19.6.
- Seis pruebas nuevas dedicadas.

## Validación ejecutada

- `ruff check .`
- `pytest -q`
- `ruff check .`: limpio.
- `pytest -q`: 6525 pruebas aprobadas.
- Baseline RP.19.6: 6519; incremento: 6 pruebas.
