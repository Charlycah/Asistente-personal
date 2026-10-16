# ROBY M311 — Conversación ambiental más segura

## Objetivo

Reducir respuestas provocadas por fragmentos del televisor o ruido ambiente sin
modificar las funciones estables de voz continua, Gmail, clima y actualidad
verificada de M310.

## Cambios

- Filtro conservador de fragmentos ambientales en `VoiceSessionGate`.
- Se descartan frases cortas de baja información como `y no fue` o
  `es una este fuimos en el` antes de enviarlas al runtime conversacional.
- Los saludos y solicitudes reconocibles de correo, clima, noticias, política y
  deportes continúan aceptándose normalmente.
- Una frase pronunciada explícitamente con la palabra de activación no se
  descarta por el filtro ambiental.
- Los avisos proactivos esperan a que termine una respuesta en curso.
- La captura de audio se pausa mientras Roby pronuncia un aviso proactivo, para
  evitar realimentación de su propia voz.

## Compatibilidad

No se cambió la inicialización de Gmail, la búsqueda de actualidad, OpenWeather,
Vosk ni el resto del runtime certificado.

## Validación

- Compilación completa correcta.
- Pruebas específicas M311 aprobadas.
- Suite completa: 6996 pruebas aprobadas.
