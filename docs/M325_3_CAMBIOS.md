# M325.3 — Executive Notification Broker

## Objetivo

Agregar una capa de política ejecutiva entre el coordinador tipado y la futura
presentación, sin modificar todavía `Queue[str]`, el desktop ni los residentes.

## Incorporado

- `core.executive_notification_broker.ExecutiveNotificationBroker`.
- Admisión exclusiva de `CoordinatedEvent`.
- Selección por prioridad descendente.
- Desempate FIFO por secuencia del coordinador.
- Expiración activa al admitir y antes de despachar.
- Deduplicación semántica conservadora basada únicamente en `entity_id` o
  `correlation_id` explícitos.
- Estados inmutables `queued`, `dispatching`, `dispatched`, `expired` y
  `duplicate`.
- Reintento seguro cuando un handler falla.
- Protección contra despacho simultáneo o reentrante.
- Snapshot operacional con resultados de política.
- Adaptador `coordinator_handler()` para encadenar M325.2 con M325.3 sin cambiar
  el runtime de producción.
- Pruebas focales M325.3.

## Deliberadamente fuera de alcance

- Integración con `Queue[str]` del desktop.
- Migración de residentes.
- Confirmación real de presentación o voz.
- Persistencia del broker.
- Fusión o coalescing de eventos relacionados.
- Presencia, interrupciones y atención.
- Recuperación automática.

Estas capacidades corresponden a los siguientes hitos de M325.
