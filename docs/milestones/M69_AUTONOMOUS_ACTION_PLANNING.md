# M69 — Autonomous Action Planning

## Objetivo

M69 introduce planificación autónoma limitada: ROBY puede reconocer que una
petición natural requiere una o varias capacidades externas y proponer un plan de
acción auditable, sin ejecutar herramientas por su cuenta.

Este milestone conecta la comprensión semántica de capacidades con la capa de
permisos y el Tool Gateway, manteniendo el principio rector de la Fase VI:

> ROBY no usa herramientas directamente. ROBY solicita capacidades y propone
> acciones revisables.

## Componentes

- `core/autonomous_action_planning.py`
- `AutonomousActionPlanningManager`
- `AutonomousActionPlanningPolicy`
- `AutonomousActionStep`
- `AutonomousActionPlan`
- `AutonomousActionPlanningSnapshot`
- `tests/test_m69_autonomous_action_planning.py`

## Reglas de diseño

- M69 no ejecuta herramientas.
- Toda acción se expresa como propuesta revisable.
- Las capacidades sensibles conservan consentimiento explícito.
- El `CognitivePipeline` solo observa snapshots y expone contexto al prompt.
- El `ToolGateway` sigue siendo la única puerta de ejecución.

## Flujo

```text
Usuario
  ↓
Capability Registry
  ↓
Permissions & Consent
  ↓
Tool Gateway Snapshot
  ↓
Autonomous Action Planning
  ↓
Plan propuesto / pendiente de consentimiento
```

## Casos cubiertos

- Clima: proponer consulta de clima antes de responder consejos prácticos.
- Correo lectura: proponer revisión o resumen de mensajes.
- Correo acción: proponer borrador/respuesta sujeta a confirmación.
- Cámara: proponer captura local con consentimiento de dispositivo.
- Combinación: coordinar varias capacidades en un único plan.

## Garantías

- No hay ejecución directa.
- No se envían correos automáticamente.
- No se abre cámara automáticamente.
- No se invocan APIs desde el pipeline.
- La salida queda normalizada y auditable.

## Validación

- Tests M69: 12 casos.
- Suite completa local: 733 pruebas en verde.
