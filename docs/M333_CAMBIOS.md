# M333 — Contrato de estado cognitivo

## Objetivo

Definir un contrato mínimo, inmutable y desacoplado para representar el estado
cognitivo de alto nivel de Roby.

## Archivos agregados

- `core/cognitive_state_contract/__init__.py`
- `core/cognitive_state_contract/models.py`
- `tests/test_m333_cognitive_state_contract.py`

## Contratos incorporados

- `CognitiveState`
- `CognitiveStateReader`

El estado expone únicamente:

- objetivo activo;
- foco actual;
- confianza;
- última decisión;
- fecha de actualización.

## Límites deliberados

M333 no agrega persistencia, escritura, historial, inferencia, aprendizaje ni
integración con el runtime. Tampoco modifica el `GlobalCognitiveState` existente.

## Compatibilidad

El cambio es aditivo. Ningún componente estable fue modificado y el nuevo paquete
puede permanecer sin uso hasta que una versión posterior incorpore persistencia.
