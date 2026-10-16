# Escucha continua de ROBY

ROBY usa el reconocimiento local de Windows (`System.Speech`) y no envía el audio del micrófono a Internet.

La configuración está en `.roby/config.json`, dentro de `services.voice.continuous_listening`.

- `enabled`: activa o desactiva la escucha.
- `wake_word`: palabra para hablarle directamente a ROBY.
- `ambient_comments`: permite comentarios espontáneos ante frases claramente relevantes.
- `comment_cooldown_seconds`: evita interrupciones frecuentes.

ROBY no responde a toda conversación. Sin la palabra “ROBY”, solo interviene ante expresiones como “¿qué hacemos?”, “no sé qué hacer”, “¿qué opinás?” o “me preocupa”.

Para privacidad, cambiá `enabled` y `ambient_audio_consent` a `false`.
