# M306.1 — Diagnóstico visible de voz y prioridad conversacional

- Muestra el tipo concreto de motor de entrada de voz en la interfaz.
- Expone las etapas: worker iniciado, llamada a start(), start completado, espera de audio/transcripción y texto reconocido.
- Conserva los eventos del motor para mostrar apertura del micrófono, nivel, voz o errores.
- Evita que preguntas personales dirigidas a ROBY, como "cómo está ROBY", se enruten a noticias.
- Mantiene intacta la búsqueda web cuando el pedido de noticias o actualidad es explícito.
