# M347.4 — Clasificación explícita de intención

## Objetivo

Hacer explícita la forma conversacional de cada turno sin crear un clasificador paralelo ni modificar la autoridad cognitiva existente.

## Implementación

Se amplió exclusivamente `CognitiveIntentAnalyzer`, la autoridad canónica ya utilizada por la memoria y la estrategia conversacional. `CognitiveIntentResult` conserva la intención cognitiva histórica y ahora también expone:

- `interaction_intent`;
- `interaction_confidence`;
- `interaction_signals`.

Las formas explícitas disponibles son `question`, `command`, `follow_up`, `correction`, `social` y `unknown`.

## Gobierno arquitectónico

- No se creó otro analizador, router, gateway, memoria ni núcleo cognitivo.
- La clasificación explícita es una dimensión adicional del mismo resultado canónico.
- Los consumidores existentes siguen funcionando mediante valores predeterminados compatibles.
- No se modificaron herramientas, red, voz, persistencia ni credenciales.
- `.roby/credentials.json` permanece intacto.

## Prioridad determinística

Cuando un turno contiene señales superpuestas, la clasificación aplica este orden:

1. corrección;
2. seguimiento;
3. comando;
4. pregunta;
5. interacción social;
6. desconocida.

Esto permite interpretar correctamente frases como `Dame el pronóstico` como seguimiento y `No, me refería a mañana` como corrección.
