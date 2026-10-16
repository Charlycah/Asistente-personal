# M308.4 – cierre por parcial estable

- Conserva Vosk como backend predeterminado.
- No modifica sensibilidad, VAD ni umbrales de inicio.
- Si Vosk mantiene un texto parcial útil sin cambios durante 1200 ms, la frase se finaliza y se entrega a la conversación.
- Evita que micrófonos con ganancia automática o ruido sostenido dejen el texto atrapado en el monitor inferior.
- Nuevo ajuste: `partial_finalize_ms` / `ROBY_AUDIO_PARTIAL_FINALIZE_MS`.
