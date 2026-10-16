# ROBY XI.2 M340.7 — Agente de Tareas Inteligentes

## Nueva capacidad

- Creación de planes temporales de varios pasos.
- Seguimiento del paso actual y del progreso.
- Pausa y reanudación por sesión.
- Avance controlado paso a paso.
- Cancelación y finalización explícitas.
- Integración previa al enrutamiento conversacional normal.

## Compatibilidad

- No modifica los servicios de dictado, traducción, documentos, memoria ni salud.
- Las tareas no se guardan en memoria permanente.
- Se retiró la referencia residual a un tercer perfil en orientación de salud:
  los perfiles reconocidos son Carlos y Cristina.

## Validación esperada

- `ruff check .`
- `pytest -q`
