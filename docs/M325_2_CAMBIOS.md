# M325.2 — Executive Coordinator

## Objetivo

Introducir una autoridad transversal y determinística para recibir, secuenciar y
entregar los eventos tipados creados en M325.1, sin modificar todavía el canal de
notificaciones de producción ni el comportamiento visible de ROBY.

## Incorporado

- `core.executive_coordinator.ExecutiveCoordinator`.
- Ciclo de vida explícito `start()` / `stop()`.
- Admisión exclusiva de `ExecutiveEvent`.
- Secuencia monotónica por instancia.
- Rechazo idempotente de `event_id` duplicados.
- Cola FIFO tipada y observable.
- Suscriptores de despacho.
- Reintento seguro: si un handler falla, el evento permanece pendiente.
- Snapshot operacional inmutable con contadores y timestamps.
- Protocol `ExecutiveEventPublisher` para futuros productores.
- Pruebas focales M325.2.

## Deliberadamente fuera de alcance

- Integración con `Queue[str]` del desktop.
- Migración de residentes.
- Priorización.
- Expiración activa.
- Deduplicación semántica.
- Fusión de eventos.
- Persistencia del coordinador.
- Confirmación de presentación.
- Recuperación automática.

Estas políticas corresponden a M325.3 y versiones posteriores.
