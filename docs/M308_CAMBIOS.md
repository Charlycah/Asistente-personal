# M308 — Speech Backend Abstraction

## Cambios

- Se agregó `app/speech_backend.py` con los contratos `SpeechRecognitionBackend` y `SpeechRecognitionSession`.
- Se agregó `VoskSpeechRecognitionBackend` como implementación predeterminada y estable.
- `VoskAudioEngine` conserva su nombre y API pública, pero ahora acepta un backend opcional.
- La captura de micrófono, VAD, segmentación, normalización, diagnósticos y UI permanecen independientes del reconocedor.
- Se agregaron tres pruebas específicas de M308.

## Validación

- Suite específica de audio: 19 pruebas aprobadas.
- Suite completa: 6973 pruebas aprobadas.
- Compilación sintáctica: aprobada.
- Ruff no estaba instalado en el entorno de construcción; debe ejecutarse localmente.

## Documentación

La carpeta `docs/` no es necesaria en tiempo de ejecución. Se conserva porque ocupa poco espacio y contiene decisiones arquitectónicas, guías e historial de hitos. Puede archivarse o excluirse de una distribución final para usuarios, pero no conviene borrarla del paquete de desarrollo sin una depuración separada.
