# M308.5 — Voz suave y gramática del pronóstico

- Se redujo el umbral base de voz de 520 a 380.
- La calibración adaptativa usa un multiplicador de ruido de 2.2 en lugar de 2.8.
- La normalización eleva el objetivo a 14000 y permite una ganancia máxima de 4.0.
- Se conserva Vosk, WebRTC VAD y la entrega de parciales estables de M308.4.
- Los estados de nubosidad del pronóstico ahora se redactan como «y muy nublado» o «y parcialmente nublado», evitando «con muy nublado».
