# M308.1 — Corrección de detección de voz

- Conserva `desktop_ui.py` de la última versión entregada por Carlos.
- Mantiene Vosk como backend predeterminado y estable.
- Reduce de 30% a 10% la proporción mínima positiva de WebRTC VAD por bloque.
- Ajusta `vad_aggressiveness` de 2 a 1 y `zcr_min` de 0.005 a 0.001.
- Esto permite palabras cortas y voz suave sin aceptar señal constante como voz.
- Agrega dos pruebas de regresión del filtro de entrada.
- Elimina la copia duplicada anidada del modelo Vosk.
- Excluye credenciales, memoria, bases personales, trazas y cachés del paquete.

Validación en el entorno de construcción: 6975 pruebas aprobadas.
`ruff` debe ejecutarse en Windows porque no está instalado en el entorno de construcción.
