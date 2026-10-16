# M335 — Actualización controlada del estado cognitivo

## Objetivo

Agregar una única frontera responsable de aplicar cambios explícitos al contrato
de estado cognitivo incorporado en M333 y persistido en M334.

## Archivos agregados

- `core/cognitive_state_contract/management.py`
- `tests/test_m335_cognitive_state_management.py`
- `M335_CAMBIOS.md`

## Archivos modificados

- `core/cognitive_state_contract/__init__.py`
- `CHANGELOG.md`

## Contratos públicos

- `CognitiveStateUpdate`
- `CognitiveStateUpdater`
- `CognitiveStateManager`

## Comportamiento

- carga el snapshot actual desde un `CognitiveStateStore`;
- usa un estado vacío como base cuando aún no existe persistencia;
- modifica solamente los campos declarados explícitamente;
- permite limpiar campos opcionales usando `None`;
- valida el resultado mediante `CognitiveState` antes de persistir;
- evita escribir cuando la actualización está vacía;
- permite restablecer el estado mediante un snapshot vacío persistido;
- exige un reloj explícito y con zona horaria.

## Límites deliberados

M335 no agrega integración con el runtime, inferencia automática, historial,
aprendizaje, reglas contextuales ni actualizaciones implícitas.
