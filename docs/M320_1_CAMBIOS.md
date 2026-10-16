# M320.1 — Criterio Conversacional

## Objetivo

Incorporar un criterio conversacional mínimo y explícito en el Brain sin alterar
el enrutamiento de capacidades, los motores, la memoria, el contexto ni la
Presentation Layer pública.

## Cambios

- Nuevo `application.brain.ConversationalCriterion` puro y sin estado.
- Clasificación conservadora de saludo, cierre, continuación, pedido directo y
  conversación social.
- `UnifiedExperienceLayer` consulta el criterio para preservar saludos solo en
  turnos de saludo y resolver cierres breves ya existentes.
- Sin cambios en motores ni contratos externos.

## Pruebas

- Clasificación de saludo, continuación, pedido directo y agradecimiento.
- Integración mínima con presentación.
- Conservación del saludo cuando corresponde y eliminación cuando es redundante.

## Reversibilidad

El cambio se concentra en un módulo nuevo y una integración pequeña en
`UnifiedExperienceLayer`; puede revertirse sin afectar motores ni persistencia.
