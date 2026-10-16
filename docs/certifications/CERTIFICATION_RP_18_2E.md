# CERTIFICATION RP.18.2E

## Runtime Health & Readiness Service

Se certifica la introducción del servicio operativo de salud y readiness basado
exclusivamente en el snapshot oficial del runtime.

### Alcance

- evaluación global de readiness;
- clasificación ready, degraded, blocked, not_ready y unknown;
- evaluación declarativa por capacidad;
- dependencias residentes requeridas y opcionales;
- blockers y warnings explicables;
- integración con `OfficialROBYRuntime`;
- serialización inmutable;
- separación explícita respecto del gate advisory M162.

### Validación en el entorno de construcción

- `python -m compileall`: correcto;
- pruebas focalizadas RP.18.2C–RP.18.2E: correctas;
- suite completa: 6431 pruebas aprobadas;
- regresiones: 0.

La validación local final requiere:

```powershell
ruff check .
pytest
```
