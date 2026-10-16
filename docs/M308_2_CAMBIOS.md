# M308.2 - Entrega de frases cortas

- Se conserva Vosk como backend predeterminado.
- El inicio de frase sigue usando VAD estricto.
- El final de frase se determina por nivel RMS para que el ruido ambiente no mantenga abierta la captura.
- Se conserva el último texto parcial de Vosk como respaldo cuando `FinalResult()` llega vacío.
- Una frase corta con texto reconocido ya no se descarta por ocupar un solo bloque de audio.
- Se agregaron tres pruebas de regresión.

Validación en el entorno de construcción: 6978 pruebas aprobadas.
