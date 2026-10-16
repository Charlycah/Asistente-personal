# M302 — Precisión de reconocimiento

M302 mejora el reconocimiento local Vosk sin enviar audio fuera del equipo.

## Cambios

- Calibración automática del ruido ambiente durante los primeros 1,5 segundos.
- Umbrales adaptativos de silencio y voz.
- Eliminación de componente continua (DC offset).
- Ganancia conservadora para audio débil, limitada para evitar saturación.
- Bloques de 3200 muestras para mejor equilibrio entre latencia y estabilidad.
- Resultados parciales visibles en el monitor como `Entendiendo: ...`.
- Backend Vosk activado en la configuración local incluida.

## Prueba recomendada

Al abrir ROBY, permanecer en silencio aproximadamente dos segundos hasta ver
`Audio calibrado`. Después hablar a una distancia y volumen normales.

Frases de control:

- `Roby, decime el clima de mañana.`
- `Roby, ahora veo el mate.`
- `Roby, pará, para allá voy.`

Si el ambiente cambia mucho (ventilador, televisor, ventana abierta), reiniciar el
motor permite recalibrar el ruido.
