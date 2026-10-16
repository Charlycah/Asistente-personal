# M308.3 — Entrega de transcripción parcial

## Problema observado

Vosk mostraba correctamente el texto parcial en el pie de la interfaz, pero la frase no llegaba a la conversación. En algunos micrófonos de Windows el nivel RMS permanece por encima del umbral por ganancia automática o ruido ambiente, así que nunca se acumulaba el silencio final necesario para cerrar la frase.

## Corrección

El cierre de una frase ahora acepta cualquiera de estas señales:

- WebRTC VAD informa que el bloque ya no contiene voz.
- El nivel RMS cae por debajo del umbral adaptativo.

El comienzo de la frase sigue requiriendo detección de voz. Vosk continúa como backend predeterminado y no se alteró la interfaz pública de M308.

## Validación

- 3 pruebas nuevas de regresión.
- 6981 pruebas aprobadas.
