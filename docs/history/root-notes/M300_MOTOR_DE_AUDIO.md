# ROBY M300 — Motor de audio

M300 separa la captura de micrófono de Tkinter y del router conversacional.

## Backends

- `powershell`: conserva el reconocedor local de Windows usado por M233.
- `vosk`: abre un stream persistente con `sounddevice`, reconoce offline y emite
  nivel real, dispositivo, silencio, voz y errores hacia la interfaz mediante
  eventos seguros.

## Activar Vosk

1. Instalar `requirements-audio-engine.txt`.
2. Colocar un modelo Vosk en `.roby/models/vosk-es` o indicar otra ruta en
   `services.voice.continuous_listening.vosk_model_path`.
3. Cambiar `audio_backend` a `vosk` en `.roby/config.json`.

La interfaz mostrará el nombre real del dispositivo o el error exacto de
inicialización. El modo activo permanece 10 segundos después de escuchar la
palabra de activación, de modo que se pueden encadenar órdenes sin repetir
"Roby" en cada frase.
