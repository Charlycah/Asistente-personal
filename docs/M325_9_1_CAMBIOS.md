# M325.9.1 — Windows File URI Fix

## Objetivo

Corregir la reconstrucción de rutas locales desde documentos `file://` durante
las pruebas del renderer Folium en Windows.

## Cambio

El helper de pruebas ya no convierte `urlparse(uri).path` directamente con
`Path`. Esa operación conserva la barra inicial de una URI como
`file:///C:/...` y produce la ruta inválida `/C:/...` en Windows.

Ahora utiliza `urllib.request.url2pathname`, que aplica la conversión nativa del
sistema operativo antes de construir el `Path`.

También valida que el documento use el esquema `file`.

## Alcance

- No cambia `FoliumMapRenderer`.
- No cambia `MapDocument`.
- No cambia la URI emitida por `Path.as_uri()`.
- No modifica runtime, conversación, voz ni presentación de ventanas.
