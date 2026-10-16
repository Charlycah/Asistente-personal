# Certificación RP.19.5

## Hito

Ejecución deliberativa y seguimiento de compromisos cognitivos.

## Garantías

- Un único compromiso cognitivo activo por snapshot.
- Sin ejecución de acciones externas.
- Progreso explícito, monotónico y persistente.
- Detección configurable de estancamiento.
- Revisión de foco mediante la cola deliberativa existente.
- Finalización integrada con cierre y tombstones de RP.19.1.
- Compatibilidad de esquema con RP.19.1–RP.19.4.
- Sin scheduler, residente, lifecycle, runtime o memoria paralelos.

## Validación focalizada

- 30 pruebas RP.19.1–RP.19.5 aprobadas.
- 6 pruebas nuevas específicas de RP.19.5.

## Certificación completa

- `ruff check .`: limpio.
- `pytest -q`: 6513 pruebas aprobadas.
- Baseline RP.19.4: 6507.
- Incremento RP.19.5: 6 pruebas.
