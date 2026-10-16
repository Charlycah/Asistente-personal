# ADR-102 — Conversational Presence Engine

## Estado
Aceptado — M100.

## Contexto
M93–M99 permiten detectar, gobernar, temporizar, desarrollar, continuar y realizar una contribución conversacional. M99 produce texto final neutral al canal, pero todavía no expresa cómo debe situarse ROBY dentro del intercambio: si responde directamente, acompaña una continuidad, entra espontáneamente con prudencia o mantiene abierta la conversación.

M51 ya define presencia cognitiva general. M100 no puede reemplazarla ni duplicarla. Debe limitarse a la postura observable de una realización M99 dentro de una conversación concreta.

## Decisión
Crear `core.living_conversation.presence` como capa posterior a M99. La capa recibe una realización inmutable y produce un sobre de presencia también inmutable con:

- estado `ready`, `abstained` o `review_required`;
- postura `responsive`, `attentive`, `companionable`, `reflective` o `restrained`;
- relación de turno `direct_reply`, `follow_up`, `continuation` o `spontaneous_entry`;
- intensidad gobernada;
- señales explícitas de reconocimiento del turno previo y apertura al seguimiento;
- referencia opcional al hilo longitudinal;
- preservación exacta de fuentes y texto upstream.

M100 no modifica segmentos, no vuelve a decidir contenido, timing o gobernanza, y no entrega nada a un canal.

## Consecuencias
- La presentación futura puede interpretar presencia sin conocer M93–M99 internamente.
- M51 y M100 permanecen separados: convivencia cognitiva general frente a postura conversacional local.
- Las entradas espontáneas quedan limitadas y requieren fuentes por defecto.
- Abstención y revisión continúan propagándose de forma segura.
- Se habilita una futura capa de entrega multicanal sin acoplarla al contenido.
