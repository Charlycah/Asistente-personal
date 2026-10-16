# M16 — Contrato observable de fallos de ROBY.process()

## Objetivo

Robustecer el contrato de `ROBY.process()` frente a excepciones internas sin cambiar la semántica pública del método.

ROBY sigue propagando la excepción original, pero ahora el fallo queda registrado de forma consistente en tracing y observabilidad.

## Flujo contractual de ROBY.process()

```text
roby.process.started
request_started
↓
Session
  ├─ session.created
  └─ session.loaded
↓
session.history.append(text)
↓
ConversationController.resolve()
conversation.resolved
↓
ExecutionEngine.execute(plan)
execution.started
execution.completed
↓
ResponseLayer.build_response(plan, execution_result)
response.built
↓
state / pending_plan update
↓
roby.process.completed
request_completed
```

Ante una excepción:

```text
roby.process.started
request_started
↓
... etapa que falla ...
↓
roby.process.failed
request_failed
raise original exception
```

## Contrato validado

Ante un fallo dentro de `ROBY.process()`:

- se registra `roby.process.started`;
- se registra el evento de telemetría `request_started`;
- se registra `roby.process.failed`;
- se registra el evento de telemetría `request_failed`;
- no se registra `roby.process.completed`;
- no se registra `request_completed`;
- se propaga la excepción original.

## Invariantes del pipeline

### Éxito

En el flujo exitoso principal:

- `roby.process.started` ocurre antes de la resolución de sesión;
- la sesión se resuelve antes de `conversation.resolved`;
- `conversation.resolved` ocurre antes de `execution.started`;
- `execution.started` ocurre antes de `execution.completed`;
- `execution.completed` ocurre antes de `response.built`;
- `response.built` ocurre antes de `roby.process.completed`;
- `roby.process.completed` es el evento terminal;
- `roby.process.completed` ocurre una sola vez;
- `roby.process.failed` no ocurre.

### Fallo

En cualquier flujo fallido cubierto por M16:

- `roby.process.failed` es el evento terminal;
- `roby.process.failed` ocurre una sola vez;
- `roby.process.completed` no ocurre;
- si falla la ejecución, no se registra `execution.completed`;
- si falla la ejecución, no se registra `response.built`;
- si falla la construcción de respuesta, no se registra `response.built`.

## Casos cubiertos

### M16.1 — Fallo durante ejecución

Cuando `execution_engine.execute(plan)` falla:

- el trace incluye `execution.started`;
- no incluye `execution.completed`;
- no incluye `response.built`;
- se registra `roby.process.failed`;
- observabilidad marca la request como fallida, no completada.

### M16.2 — Fallo durante resolución conversacional

Cuando `conversation_controller.resolve(session, text)` falla:

- el input ya fue agregado a `session.history`;
- no se registra `conversation.resolved`;
- se registra `roby.process.failed`;
- observabilidad marca la request como fallida, no completada.

### M16.3 — Fallo durante construcción de respuesta

Cuando `response_layer.build_response(plan, execution_result)` falla:

- el trace incluye `execution.started` y `execution.completed`;
- no incluye `response.built`;
- se registra `roby.process.failed`;
- observabilidad marca la request como fallida, no completada.

### M16.4 — Invariantes del pipeline

Se agregan tests que protegen el orden contractual del pipeline y los eventos terminales de éxito/fallo.

### M16.5 — Documentación del contrato

Se documenta el contrato de `ROBY.process()` como referencia arquitectónica antes de abrir nuevos milestones.

## Decisión arquitectónica

No se convierte el fallo en un `UserResponse` de error en este milestone.

Ese cambio alteraría el contrato público de `ROBY.process()` y requiere un diseño separado de política de errores recuperables vs. errores propagados.

## Validación

- Tests focales ROBY/tracing/observabilidad: verdes.
- Suite ROBY pública/end-to-end/tracing/observabilidad: verde.
- Suite completa sin manual smoke de config: verde.
- Suite completa con manual smoke mantiene los fallos conocidos por ausencia de `config.example.json`.
- Ruff no ejecutable en el entorno porque el paquete no está instalado.
