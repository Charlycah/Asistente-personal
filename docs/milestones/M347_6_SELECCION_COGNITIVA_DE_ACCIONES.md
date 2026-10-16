# M347.6 — Selección cognitiva de acciones

## Objetivo

Hacer que el único `ConversationStrategyPlanner` seleccione una acción cognitiva
declarativa a partir de la intención explícita incorporada en M347.4 y utilizada
por la planificación de M347.5.

## Alcance

Se incorpora `CognitiveAction` dentro de `core/conversation_strategy.py` con las
acciones `answer`, `prepare_action`, `continue_context`, `revise_context`,
`acknowledge` y `clarify`.

La selección no ejecuta herramientas, no llama proveedores y no afirma que una
acción externa haya ocurrido. `prepare_action` expresa únicamente que el turno
es candidato a continuar por las capacidades canónicas existentes.

## Compatibilidad

Los turnos con intención interactiva explícita exponen `selected_action` en los
metadatos. Los turnos históricos sin clasificación interactiva conservan sus
metadatos exactamente iguales y seleccionan `clarify` mediante el campo tipado
de la estrategia.

## Límites

- No se crea un selector paralelo.
- No se crea otro planificador, router, gateway o núcleo cognitivo.
- No se modifican voz, red, persistencia ni ejecución.
- `.roby/credentials.json` permanece intacto.
