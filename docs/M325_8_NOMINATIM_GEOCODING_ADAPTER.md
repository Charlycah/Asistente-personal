# M325.8 — Nominatim Geocoding Adapter

## Objetivo

Incorporar un adaptador concreto de geocodificación para Nominatim detrás del
contrato `MapGeocodingProvider` introducido en M325.7.

## Alcance

- Configuración inmutable de proveedor, timeout, idioma, países y límite.
- Transporte HTTP basado exclusivamente en biblioteca estándar.
- `User-Agent`, `Accept` y `Accept-Language` explícitos.
- Traducción de resultados Nominatim a `MapDisplayTarget`.
- Caché en memoria con TTL configurable.
- Intervalo mínimo configurable entre solicitudes externas.
- Errores normalizados de timeout, rate limit, transporte y respuesta.
- Transporte, reloj y pausa inyectables para pruebas deterministas.

## Fuera de alcance

- No se integra todavía con el runtime conversacional.
- No se generan documentos HTML.
- No se agrega Folium.
- No se abren ventanas ni navegador.
- No se efectúan solicitudes reales durante las pruebas.

## Compatibilidad

M325.8 agrega infraestructura nueva sin modificar los contratos de M325.7 ni
los componentes geográficos existentes.

## Validación esperada

```text
ruff check .
All checks passed!

pytest -q
7262 passed
```
