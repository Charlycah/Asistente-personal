# M320.4 — Priorización Conversacional

## Objetivo

Priorizar la intención accionable cuando un mismo turno combina saludos,
agradecimientos, conectores sociales y un pedido concreto.

## Alcance

- Cambio localizado en `ConversationalCriterion`.
- Sin modificaciones en motores, memoria, contexto ni contratos públicos.
- Los saludos, agradecimientos y despedidas puros conservan su comportamiento.
- Un pedido explícito prevalece sobre las capas sociales que lo preceden.

## Pruebas

Se agregan casos para pedidos precedidos por múltiples cortesías y para evitar
regresiones en cierres conversacionales puros.
