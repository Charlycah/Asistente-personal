# M347.7 — Trazabilidad interna de decisiones

## Objetivo

Incorporar una traza estructurada de los hechos que participan en la decisión conversacional, dentro del planificador canónico y sin exponer razonamiento privado.

## Implementación

Se añadió `CognitiveDecisionTrace` en `core/conversation_strategy.py`. Cada estrategia producida por `ConversationStrategyPlanner` recibe una traza inmutable con:

- intención cognitiva y confianza;
- intención interactiva y confianza;
- acción cognitiva seleccionada;
- tono, profundidad y formato;
- decisión de uso del LLM;
- herramientas consideradas;
- herramienta seleccionada;
- motivo estructurado de fallback.

En este milestone no se seleccionan ni ejecutan herramientas. Por eso los campos correspondientes permanecen vacíos y verificables, evitando afirmar ejecuciones inexistentes.

## Privacidad y explicabilidad

La traza contiene hechos determinísticos. No almacena prompts, credenciales, texto sensible, deliberaciones ni cadenas de razonamiento. `as_dict()` ofrece una representación segura para diagnóstico interno futuro.

## Compatibilidad

El campo `decision_trace` usa `compare=False`, por lo que no cambia la igualdad histórica de `ConversationStrategy`. Tampoco modifica los metadatos existentes ni la respuesta producida.

## Alcance excluido

No se agregaron persistencia, logging paralelo, telemetría externa, ejecución de herramientas, red, voz, memoria ni otro planificador. `.roby/credentials.json` permanece intacto.

## Validación

Se agregaron pruebas para estructura, confianza, privacidad, fallback, ausencia de falsas ejecuciones y compatibilidad histórica.
