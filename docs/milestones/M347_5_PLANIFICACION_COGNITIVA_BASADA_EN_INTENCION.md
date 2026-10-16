# M347.5 — Planificación cognitiva basada en intención

## Objetivo

Hacer que la estrategia conversacional canónica utilice explícitamente la forma del turno clasificada en M347.4, sin crear un segundo planificador ni modificar el núcleo cognitivo único.

## Autoridad ampliada

Se amplía exclusivamente `core.conversation_strategy.ConversationStrategyPlanner`. La planificación por dominio cognitivo existente permanece como base y luego recibe un enriquecimiento determinístico según `InteractionIntent`.

## Comportamiento incorporado

- `QUESTION`: prioriza responder la pregunta explícita.
- `COMMAND`: interpreta una solicitud de acción y prohíbe afirmar ejecución inexistente.
- `FOLLOW_UP`: conserva continuidad y evita repeticiones innecesarias.
- `CORRECTION`: prioriza la corrección más reciente y descarta la interpretación corregida.
- `SOCIAL`: responde de forma natural y proporcionada.
- `UNKNOWN`: mantiene exactamente la estrategia histórica, sin agregar metadatos.

La estrategia conserva tono, profundidad, formato y decisión de uso de LLM definidos por la intención cognitiva de dominio. La intención interactiva solo enriquece `system_hints` y `metadata`.

## Compatibilidad

Los consumidores que construyen `CognitiveIntentResult` sin los campos M347.4 continúan recibiendo la misma estrategia y los mismos metadatos históricos.

## Límites

M347.5 no agrega ejecución, herramientas, red, memoria, persistencia, autonomía, otro clasificador, otro planificador ni otro gateway. `.roby/credentials.json` permanece intacto.

## Validación focalizada

Las pruebas cubren preguntas, comandos, seguimientos, correcciones, interacciones sociales, casos desconocidos, confianza expuesta y regresión del planificador histórico.
