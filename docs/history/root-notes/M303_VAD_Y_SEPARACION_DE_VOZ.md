# ROBY XI.2 M303 — VAD y separación de voz

Esta versión reduce la mezcla entre la voz del usuario, la televisión y el ruido
ambiente antes de enviar audio a Vosk.

## Cambios principales

- VAD WebRTC opcional, con fallback adaptativo RMS + cruces por cero.
- Pre-roll de 300 ms para conservar las primeras sílabas.
- Cierre de frase por silencio sostenido.
- Duración mínima de voz para descartar ruidos breves.
- Límite de duración por frase para evitar transcripciones interminables.
- Recalibración automática del ruido durante silencios prolongados.
- El wake word puede aparecer después de un saludo corto, por ejemplo:
  `hola, cómo te va, Roby, decime el clima`.
- Nuevos controles de configuración y tests M303.

## Instalación del VAD recomendado

```powershell
pip install -r requirements-audio-engine.txt
```

Si `webrtcvad-wheels` no está disponible, ROBY continúa funcionando con el VAD
adaptativo incluido.

## Prueba sugerida

1. Iniciar ROBY con la televisión encendida a volumen habitual.
2. Esperar la calibración inicial sin hablar.
3. Decir con una pausa breve al final:
   `Roby, cómo está el clima`.
4. Probar también:
   `Hola Roby, decime la hora`.
5. Confirmar que la televisión puede generar actividad visual, pero no órdenes,
   salvo que diga el wake word al comienzo de una frase.

## Ajustes útiles

- `vad_aggressiveness`: 0 a 3. Un valor mayor filtra más ruido y TV.
- `end_silence_ms`: silencio requerido para cerrar una frase.
- `pre_roll_ms`: audio conservado antes de detectar voz.
- `voice_threshold`: energía mínima absoluta.
- `noise_multiplier`: sensibilidad respecto del ruido calibrado.
