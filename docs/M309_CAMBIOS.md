# M309 — Entrega directa de voz reconocida

- La escucha continua ya no exige decir «Roby» antes de cada petición.
- Todo comando reconocido con al menos dos palabras se entrega al runtime conversacional.
- La palabra de activación sigue disponible y puede volver a exigirse configurando `require_wake_word` en `true`.
- Se conserva el filtro de fragmentos de una sola palabra para evitar respuestas ante ruidos aislados.
