# RP.04 — Natural Conversation Flow

RP.04 refina el flujo visible de las respuestas sin modificar el runtime
cognitivo ni incorporar capas arquitectónicas.

## Cambios

- Varía conectores discursivos consecutivos idénticos dentro de una misma
  respuesta.
- Reduce separaciones verticales excesivas a un único salto de párrafo.
- Conserva código inline y bloques fenced de forma literal.
- Registra ambos ajustes en la telemetría del refinamiento conductual.

## Límites

La política no reescribe contenido semántico, no introduce aleatoriedad y no
modifica listas, comandos, citas ni datos técnicos protegidos.
