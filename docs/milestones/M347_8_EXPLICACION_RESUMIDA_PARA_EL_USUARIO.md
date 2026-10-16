# M347.8 — Explicación resumida para el usuario

## Objetivo

Permitir que ROBY describa de forma breve y segura cómo abordó un turno, reutilizando la trazabilidad interna de M347.7 y sin revelar razonamiento privado.

## Implementación

`CognitiveDecisionTrace.explain_for_user()` transforma la acción cognitiva ya seleccionada en una frase determinística y comprensible. `ConversationStrategy.explain_decision_for_user()` actúa como acceso opcional y devuelve `None` para estrategias históricas sin traza.

La explicación cubre seis resultados observables:

- responder una consulta;
- preparar una solicitud de acción sin afirmar ejecución;
- continuar con el contexto anterior;
- revisar el contexto por una corrección;
- reconocer un intercambio social;
- priorizar una aclaración.

## Fuente de verdad

No se almacena un nuevo campo de explicación. El texto se deriva bajo demanda de `selected_action`, ya presente en `CognitiveDecisionTrace`. De este modo la traza sigue siendo la única fuente de verdad y no aparece estado duplicado.

## Privacidad

La explicación no contiene prompts, credenciales, datos sensibles, hipótesis descartadas, deliberaciones ni cadenas de razonamiento. Solo comunica el resultado observable de la decisión.

## Compatibilidad

No cambian el planificador, los metadatos, la igualdad histórica, el runtime ni la respuesta principal. Una estrategia construida sin traza mantiene el comportamiento previo y devuelve `None` al solicitar una explicación.

## Alcance excluido

No se agregaron routers, planificadores, memorias, logging paralelo, persistencia, red, voz, selección de herramientas ni ejecución. `.roby/credentials.json` permanece intacto.

## Validación

Se añadieron pruebas para preguntas, comandos, seguimientos, correcciones, intercambios sociales, casos desconocidos, privacidad, ausencia de afirmaciones falsas de ejecución y compatibilidad histórica.
