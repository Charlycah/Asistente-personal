# M17 — Internal Event Publisher

## Objetivo

Introducir una capa interna de publicación de eventos para desacoplar `ROBY.process()` de los consumidores concretos de tracing y observabilidad.

El comportamiento público de ROBY no cambia. Los tests existentes de tracing, observabilidad, API pública y end-to-end siguen pasando.

## Decisión arquitectónica

Se incorpora una abstracción específica para eventos internos de ROBY:

```text
ROBY.process()
    ↓
InternalEvent
    ↓
EventPublisher
    ↓
Subscribers
    ├─ TraceEventSubscriber
    └─ TelemetryEventSubscriber
```

ROBY ya no necesita llamar directamente a:

```text
trace_recorder.record(...)
observability.record_event(...)
```

En su lugar publica eventos internos mediante:

```text
self.event_publisher.publish(InternalEvent(...))
```

## Componentes agregados

### InternalEvent

Evento interno inmutable con:

- `name`;
- `component`;
- `channel`;
- `metadata`.

### EventChannel

Canales soportados:

- `TRACE`;
- `TELEMETRY`.

### EventPublisher

Protocolo mínimo:

```python
publish(event: InternalEvent) -> None
```

### EventSubscriber

Protocolo mínimo:

```python
handle(event: InternalEvent) -> None
```

### CompositeEventPublisher

Publicador compuesto que distribuye un evento a todos sus subscribers.

### TraceEventSubscriber

Consume únicamente eventos `TRACE` y los delega al `TraceRecorder` existente.

### TelemetryEventSubscriber

Consume únicamente eventos `TELEMETRY` y los delega al `ObservabilityCollector` existente convirtiéndolos a `TelemetryEvent`.

## Compatibilidad

El constructor de `ROBY` mantiene compatibilidad con:

- `trace_recorder`;
- `observability`.

Si no se provee `event_publisher`, ROBY crea uno por defecto con:

```text
CompositeEventPublisher([
    TraceEventSubscriber(trace_recorder),
    TelemetryEventSubscriber(observability),
])
```

Además, se puede inyectar un `event_publisher` custom para tests, auditoría, logging o futuros plugins.

## Tests agregados

- `CompositeEventPublisher` despacha a todos los subscribers.
- `TraceEventSubscriber` ignora eventos que no sean de tracing.
- `TelemetryEventSubscriber` ignora eventos que no sean de telemetría.
- `ROBY.process()` publica eventos de tracing y telemetría a través del `EventPublisher`.

## Invariantes preservadas

- El orden de eventos de tracing de M16 se mantiene.
- Los contadores de observabilidad se mantienen.
- `request_completed` no se emite ante fallos.
- `roby.process.failed` se mantiene como evento terminal de fallo.
- `roby.process.completed` se mantiene como evento terminal de éxito.

## Alcance intencionalmente excluido

M17 no introduce todavía:

- persistencia de eventos;
- logging estructurado;
- auditoría;
- memoria basada en eventos;
- plugins;
- cambios en la interfaz pública de `ROBY.process()`.

Es un refactor arquitectónico transparente para preparar esos milestones futuros.

## Validación

- Tests M17: verdes.
- Tests focales ROBY/tracing/observabilidad/pública/end-to-end: verdes.
- Suite completa sin manual smoke de config: verde.
- Suite completa con manual smoke mantiene los fallos conocidos por ausencia de `config.example.json`.
- Ruff no ejecutable en el entorno porque el paquete no está instalado.
