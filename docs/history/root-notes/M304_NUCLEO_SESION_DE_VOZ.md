# M304 — Núcleo de sesión de voz

M304 agrega una compuerta estricta entre la transcripción local y el motor
conversacional.

- Fuera de una sesión activa, sólo se acepta una frase que incluya `Roby` o
  una variante configurada.
- `Hola Roby` abre una ventana breve para decir el comando a continuación.
- Una orden completa como `Roby, cómo está el clima` se procesa de inmediato.
- Las voces de TV y otras conversaciones se descartan y no aparecen como
  mensajes `Vos:`.
- Los fragmentos de una sola palabra se descartan.
- Mientras ROBY procesa o habla, el motor de audio queda pausado y vacía las
  colas para evitar realimentación y transcripciones atrasadas.

Configuración:

- `ROBY_VOICE_ACTIVE_WINDOW_SECONDS` (predeterminado: 8)
- `ROBY_VOICE_MIN_COMMAND_WORDS` (predeterminado: 2)
- `ROBY_VOICE_WAKE_ALIASES`
