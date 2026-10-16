# M325.12 — Map Clarification Follow-up

Base: M325.11 estable (`ruff check .` limpio, 7339 pruebas OK).

## Cambios

- Conserva por sesión hasta tres resultados ambiguos del geocoder.
- Acepta selecciones por número, ordinal o fragmento único del nombre.
- Permite cancelar la selección pendiente.
- Expira el contexto de aclaración mediante una política configurable.
- Aísla el estado por `session_id` y limita la cantidad de sesiones pendientes.
- No captura mensajes ajenos a mapas mientras espera una selección.
- Actualiza el identificador local de Nominatim a M325.12.

## Variables y valores predeterminados

- Tiempo de aclaración: 300 segundos.
- Máximo de sesiones pendientes: 32.
- Máximo de opciones conversacionales: 3.

## Validación esperada

```powershell
ruff check .
pytest tests/test_m325_12_map_clarification_follow_up.py -q
pytest -q
```
