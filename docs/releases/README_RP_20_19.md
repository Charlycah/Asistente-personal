# RP.20.19 — Retiro de delegador puro en servicio interno

Se retiró `ReminderService.list_overdue()`. El método no tenía consumidores y se limitaba a ejecutar `self.list_due(reminders, now)`, sin añadir política, transformación, validación, coordinación ni estado.

Se conserva `ReminderService` porque sus operaciones canónicas sí implementan consultas de dominio:

- `list_due()` filtra recordatorios pendientes vencidos y los ordena;
- `list_for_day()` filtra por día y estado;
- `list_next()` selecciona próximos recordatorios, ordena y aplica límite.

La auditoría también revisó fachadas, managers, coordinadores y servicios internos. Se conservaron aquellos que aplican reglas, normalizan entradas, coordinan colaboradores, mantienen estado o protegen fronteras externas.

Validación esperada:

```powershell
ruff check .
pytest -q
```
