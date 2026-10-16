# M306 — Integración real del motor de voz

- Inicia explícitamente el motor de audio antes del ciclo continuo de transcripción.
- Conserva `start`, `stop`, `set_paused`, `set_event_sink` y `error` al usar `SafeVoiceInput`.
- Muestra en la interfaz los errores reales de apertura o ejecución del micrófono.
- Evita que el worker termine silenciosamente.
- Mantiene todas las actualizaciones de Tkinter en el despachador del hilo de UI.
- Añade pruebas de regresión para el ciclo de vida del motor de voz.
