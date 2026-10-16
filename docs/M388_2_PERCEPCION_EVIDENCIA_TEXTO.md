# M388.2 — Percepción y evidencia para el canal texto

## Propósito

M388.2 conecta `perception_and_evidence` mediante el único canal universalmente
real en el recorrido actual: texto interactivo recibido por la entrada oficial.

## Evidencia admitida

La evidencia confirma únicamente:

- presencia de texto no vacío;
- origen declarado;
- envío interactivo al gateway oficial.

No copia el mensaje, no interpreta su significado y no lo convierte en hecho.

## Canales

`internal` y `desktop_text` participan como texto certificado. Un payload textual
originado en voz, consola histórica, Android, sensores u otro origen queda
degradado hasta que ese canal posea certificación propia. La existencia de una
transcripción no certifica micrófono, voz, cámara o hardware.

## Orden del ciclo

La percepción se registra antes del runtime conversacional. Por eso incluso una
falla posterior conserva el hecho mínimo de que entró texto. En un turno con
identidad confirmada, el prefijo conectado avanza hasta percepción y la primera
brecha pasa a `memory_recall`.

## Límites

M388.2 no clasifica el contenido como hecho, inferencia o hipótesis; esa tarea
pertenece a una etapa epistemológica posterior. Tampoco lee archivos, activa
dispositivos, solicita permisos, guarda mensajes ni ejecuta acciones.

La línea base M388.1 permanece congelada como corte posterior a M387. La nueva
participación puede medirse en sus campos operacionales sin reescribir ese punto
histórico.
