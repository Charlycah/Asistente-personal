# M387.7 — Respuesta y acciones externas

## Propósito

M387.7 incorpora evidencia separada para composición de respuesta y compuerta
de acción. Responder no implica actuar y una acción no se declara ejecutada por
el solo hecho de haber sido propuesta.

## Respuesta

El nodo `response_composition` distingue respuestas completadas, parciales,
retenidas, no aplicables y fallidas. Las respuestas locales controladas, como la
identificación del interlocutor, también quedan registradas sin copiar su texto.

## Acción

El nodo `action_gate` observa dos fronteras existentes:

- `ToolGateway`: un comando explícito enrutado puede demostrar participación;
  bloqueo o fallo conservan su estado real.
- `OfficialCapabilityGateway`: una capacidad interna no reclama efecto externo.
  Una capacidad con ámbito externo queda degradada si la frontera genérica no
  puede demostrar por sí sola el consentimiento específico aplicado.

Esta degradación es intencional: evita certificar permisos basándose únicamente
en metadatos declarativos.

## Privacidad y autoridad

La evidencia no contiene respuestas, salidas de herramientas, payloads,
capacidades concretas, nombres o sesiones. El adaptador no ejecuta herramientas,
no concede permisos y no modifica resultados.

## Evolución del diagnóstico

Los turnos locales identificados ahora demuestran también
`response_composition`. La cadena inicial continua sigue terminando en
`identity_and_context`, porque `perception_and_evidence` aún no aporta evidencia.
