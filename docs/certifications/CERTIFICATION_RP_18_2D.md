# Certificación RP.18.2D — Snapshot operativo unificado del runtime

## Alcance certificado

- Modelo operativo inmutable y serializable.
- Integración oficial con lifecycle, supervisor y registro residente.
- Clasificación global de estado, salud y disponibilidad.
- Conteos residentes y causas normalizadas de degradación.
- Ausencia de instancias residentes en la vista pública.
- Preservación de APIs y comportamiento anteriores.

## Validación ejecutada en el entorno de integración

```text
Pruebas focalizadas: 30 passed
Suite completa:      6418 passed
compileall:           correcto
```

Ruff no se encuentra instalado en el contenedor de integración. Debe ejecutarse en el entorno local certificado:

```powershell
ruff check .
pytest
```

## Resultado

RP.18.2D queda funcionalmente integrada, sin regresiones observadas.
