# RP.24.7 — Audio Inteligente

Esta etapa incorpora el plano de control de audio gobernado de ROBY.

## Alcance

- Modos deshabilitado, pulsar para hablar, palabra de activación y escucha
  continua autorizada.
- Validación explícita de permiso de micrófono y consentimiento.
- Compuerta de actividad de voz y confianza.
- Sesiones temporales con vencimiento por inactividad.
- Cola acotada de expresiones autorizadas.
- Eventos auditables con identificadores estables.

## Límite de seguridad

El servicio no abre el micrófono, no graba audio y no inicia proveedores. Recibe
señales ya obtenidas por adaptadores autorizados y decide si pueden incorporarse
a la conversación.
