# M336 — Historial limitado de transiciones cognitivas

## Objetivo

Agregar un historial acotado y auditable de las transiciones explícitas producidas
por el administrador de estado cognitivo de M335.

## Archivos agregados

- `core/cognitive_state_contract/history.py`
- `tests/test_m336_cognitive_state_transition_history.py`
- `M336_CAMBIOS.md`

## Archivos modificados

- `core/cognitive_state_contract/management.py`
- `core/cognitive_state_contract/__init__.py`
- `CHANGELOG.md`

## Contratos públicos

- `CognitiveStateTransition`
- `CognitiveStateTransitionStore`
- `JsonCognitiveStateTransitionStore`

## Comportamiento

- representa cada transición mediante snapshots inmutables anterior y posterior;
- distingue transiciones de actualización y reinicio mediante una razón validada;
- almacena el historial en `.roby/cognitive_state_history.json` por defecto;
- mantiene el historial separado del snapshot cognitivo vigente;
- aplica una capacidad configurable, de 50 entradas por defecto;
- elimina primero las transiciones más antiguas al superar la capacidad;
- devuelve resultados en orden cronológico;
- permite consultar solamente las transiciones más recientes;
- escribe el documento JSON de forma atómica;
- permite limpiar el historial explícitamente;
- registra una transición únicamente después de persistir el nuevo estado;
- no registra actualizaciones vacías ni intentos cuya persistencia falla.

## Compatibilidad

El parámetro `transition_store` de `CognitiveStateManager` es opcional. Las
construcciones y comportamientos de M335 continúan funcionando sin cambios cuando
no se proporciona un almacén de transiciones.

## Límites deliberados

M336 no integra el historial con el runtime, no genera transiciones automáticas,
no interpreta su contenido, no aprende de él y no ejecuta acciones autónomas.

## Validación del entorno de construcción

- pruebas específicas M333–M336: 58 aprobadas;
- pruebas nuevas de M336: 18;
- suite completa: 7809 aprobadas;
- `compileall`: aprobado;
- Ruff pendiente de validación local porque no está instalado en el contenedor.
