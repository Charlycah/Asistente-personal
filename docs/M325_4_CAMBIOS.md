# M325.4 — Presence & Attention Manager

## Objetivo

Agregar una autoridad tipada y determinista que evalúe si un evento ejecutivo
puede entregarse, debe diferirse o debe silenciarse según presencia y atención.

## Incorporado

- `PresenceAttentionManager` en memoria y thread-safe.
- Estados explícitos de presencia y atención.
- Decisiones `DELIVER`, `DEFER` y `SILENCE` con motivo auditable.
- Excepción controlada para eventos `CRITICAL`.
- Integración optativa con `ExecutiveNotificationBroker`.
- Conservación de eventos diferidos para una evaluación posterior.
- Eliminación contabilizada de eventos silenciados.
- Snapshots inmutables del manager y nuevos contadores del broker.

## Compatibilidad

Sin `attention_decider`, el broker conserva exactamente la política de M325.3.
No se modifican residentes, desktop, voz, presentación ni `Queue[str]`.

## Fuera de alcance

- Inferencia automática de presencia mediante sensores.
- Persistencia de estados y decisiones.
- Ventanas temporales o calendarios de silencio.
- Confirmación de presentación o reproducción de voz.
- Migración de residentes al flujo ejecutivo.
