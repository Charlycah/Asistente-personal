# M347.10 — Modelo explícito de contexto conversacional

## Objetivo

Introducir una representación explícita, estructurada e inmutable del contexto
conversacional inmediato dentro del flujo cognitivo canónico. El contexto aporta
hechos al único `ConversationStrategyPlanner`; no clasifica, decide, ejecuta ni
persiste información por sí mismo.

## Implementación

Se añadió `ConversationContext` en `core/conversation_strategy.py`, junto a las
autoridades que lo consumen. El modelo representa de forma mínima:

- tema activo;
- entidades activas;
- intención cognitiva anterior;
- intención interactiva anterior;
- acción cognitiva anterior;
- referencia pendiente;
- objetivo de una corrección;
- posición del turno.

`ConversationStrategyPlanner.plan()` acepta un contexto opcional. Cuando existe
información previa, la integra en la estrategia mediante indicaciones y metadatos
seguros. La misma instancia queda disponible en `ConversationStrategy` y en
`CognitiveDecisionTrace`, evitando copias divergentes y fuentes paralelas.

## Límites deliberados

M347.10 no incorpora todavía:

- resolución automática de referencias;
- reconstrucción de contexto desde historial;
- memoria persistente;
- selección semántica de recuerdos;
- escritura, consolidación o deduplicación de memoria;
- otro gestor, router, planificador o núcleo.

El contexto vacío es válido y conserva el comportamiento histórico. La nueva
información no participa de la igualdad de `ConversationStrategy`, por lo que
las estrategias anteriores siguen siendo compatibles.

## Seguridad y privacidad

La serialización del contexto contiene únicamente hechos estructurados. No
incluye historial completo, prompts, texto libre del usuario, credenciales ni
razonamiento privado. `.roby/credentials.json` no fue modificado.

## Validación específica

`tests/test_m347_10_explicit_conversation_context.py` verifica:

- contexto vacío seguro;
- inmutabilidad;
- representación estructurada;
- consumo por el planificador canónico;
- uso de la misma instancia en estrategia y traza;
- ausencia de resolución prematura;
- compatibilidad sin contexto;
- igualdad histórica.
