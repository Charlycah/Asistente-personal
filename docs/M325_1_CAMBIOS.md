# M325.1 — Executive Event Model

## Objetivo

Introducir un contrato común de eventos tipados sin modificar todavía el flujo visible de ROBY ni reemplazar `Queue[str]`.

## Cambios

- Se agregó `core/executive_event_model`.
- Se creó `ExecutiveEvent`, inmutable y con metadata común.
- Se agregaron enums de tipo, origen, prioridad, privacidad y entrega.
- Se incorporó el catálogo inicial:
  - `GenericTextEvent`
  - `BatteryLowEvent`
  - `ReminderDueEvent`
  - `AmbientObservationEvent`
  - `VerifiedNewsEvent`
  - `ImportantEmailEvent`
  - `VisualCaptureResultEvent`
- Se agregó serialización versionada y reconstrucción por tipo concreto.
- Se agregó validación de timestamps, identidad, expiración y payload JSON.
- Se agregó el adaptador temporal `text_to_executive_event()`.
- Se agregaron pruebas focales en `tests/test_m325_1_executive_event_model.py`.

## Compatibilidad

- No se modificó `app/desktop_bootstrap.py`.
- No se reemplazó `Queue[str]`.
- No se introdujeron prioridad ejecutiva, deduplicación, expiración automática ni coordinación.
- Los residentes conservan su comportamiento M324.
