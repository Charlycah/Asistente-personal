# M325.6 — Runtime Executive Integration

## Objetivo

Convertir las capas ejecutivas M325.1–M325.5 en el camino interno real de las
notificaciones del desktop, preservando la interfaz textual existente.

## Cambios

- Se agregó `core/executive_runtime_integration/`.
- Las notificaciones heredadas se adaptan a `GenericTextEvent`.
- El flujo real pasa por `ExecutiveCoordinator` y
  `ExecutiveNotificationBroker`.
- `PresenceAttentionManager` recibe señales de escritura, voz y respuesta.
- `RecoveryHealthCoordinator` observa coordinador, broker y presentación.
- La UI sigue recibiendo `tuple[str, ...]` mediante un adaptador terminal.
- Los residentes y sus contratos públicos no fueron reescritos.

## Flujo

```text
resident notify(str)
→ GenericTextEvent
→ ExecutiveCoordinator
→ ExecutiveNotificationBroker
→ PresenceAttentionManager
→ adaptador de presentación textual
→ ROBYDesktopApp
```

## Compatibilidad

`Queue[str]` deja de ser el canal central compartido. Sólo permanece una cola
privada dentro del adaptador terminal de presentación, por lo que el contrato
de drenaje de la UI continúa intacto.
