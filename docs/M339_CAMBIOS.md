# M339 — Objetivos cognitivos activos

Base oficial: M338 validada con 7848 pruebas.

## Alcance

M339 incorpora una colección explícita y determinista de objetivos cognitivos.
No añade planificación, ejecución automática, inferencia ni integración con el
runtime.

## Nuevo paquete

`core/cognitive_goals/`

API pública:

- `CognitiveGoal`
- `GoalStatus`
- `GoalPriority`
- `GoalCollection`
- `GoalResolver`
- `PriorityGoalResolver`
- `GoalController`
- `GoalManager`

## Reglas

- Los identificadores son únicos.
- Los objetivos pueden estar activos, pausados, completados o cancelados.
- Solo los objetivos activos participan en la selección.
- Gana la prioridad más alta.
- Ante empate, gana el objetivo más antiguo.
- El identificador actúa como desempate final determinista.
- Solo el título del objetivo principal se refleja en
  `CognitiveState.active_objective`.
- Si el objetivo principal no cambia, no se escribe el estado cognitivo.
- Si falla la escritura del estado, la colección local no se modifica.

## Operaciones

- agregar
- eliminar
- pausar
- reanudar
- completar
- cancelar
- consultar todos los objetivos
- consultar objetivos activos
- consultar objetivo principal

## Compatibilidad

No se modifica el esquema JSON existente y no se crea un archivo de
persistencia nuevo. Los cambios del objetivo principal reutilizan la
actualización controlada, persistencia e historial de M334–M336.

## Pruebas

Archivo nuevo:

`tests/test_m339_cognitive_goals.py`

- 26 pruebas nuevas.
- 123 pruebas del bloque M333–M339 aprobadas.
- Suite completa: 7874 pruebas aprobadas.
