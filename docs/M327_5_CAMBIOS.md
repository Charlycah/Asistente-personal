# ROBY XI.2 — M327.5

## Notificación clara del resultado autónomo

M327.5 incorpora una presentación explícita para los resultados de capacidades
autónomas que realmente fueron ejecutadas por el runtime.

### Alcance

- Traduce el resultado técnico del ciclo autónomo a un mensaje breve en español.
- Informa qué comprobación realizó Roby y cuál fue el resultado observado.
- Explica expresamente cuando no se realizaron cambios automáticos.
- Incluye el detalle del error de audio cuando está disponible.
- Presenta resultados de diagnóstico de audio y de verificación de salud.
- No notifica ciclos sin situación, no autorizados o no ejecutados.
- Registra en el snapshot la cantidad de notificaciones autónomas generadas.
- Entrega la notificación mediante la cola existente del runtime y la interfaz.

### Seguridad

Esta versión no modifica políticas, permisos, umbrales, acciones disponibles ni
mecanismos de ejecución. Solamente presenta al usuario resultados que ya fueron
producidos y supervisados por el sistema de autonomía controlada.

### Pruebas

Se agregan tres pruebas para cubrir:

1. Notificación de un diagnóstico de audio operativo.
2. Explicación de una degradación con detalle y límites de actuación.
3. Notificación de la verificación autónoma de un componente del runtime.
