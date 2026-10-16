# ROBY XI.2 — RP.20.15

## Limpieza de superficies agregadas en `__init__.py`

Esta revisión elimina dos APIs de comodidad interna que sólo agregaban símbolos de módulos propietarios:

- `m4.__init__`
- `m5.handlers.__init__`

Los consumidores internos fueron migrados a imports canónicos:

- `m4.context_builder.ContextBuilder`
- `m4.decision_engine.DecisionEngine`
- `m4.models.EngineType`, `PlanType`, `Priority`
- `m4.router.PlanRouter`
- `m5.handlers.reminder_handler.ReminderExecutionHandler`

No se retiraron constantes: la auditoría no encontró duplicaciones aisladas con evidencia suficiente para una eliminación segura.

## Certificación de preparación

- `ruff check .`: correcto
- `pytest -q`: 6566 passed
