# M325.7 Map Display Contracts

## Objetivo

Incorporar contratos puros para la futura visualización de ubicaciones sin agregar
geocodificación real, generación HTML, ventanas gráficas ni nuevas dependencias.

## Alcance

- Solicitud normalizada de visualización de mapa.
- Objetivo geográfico resuelto.
- Documento HTML de mapa.
- Resultado estructurado de presentación.
- Resultado integral de visualización.
- Puertos sustituibles para geocodificación, renderizado y presentación.

## Fuera de alcance

- Nominatim o cualquier llamada de red.
- Folium.
- pywebview o apertura del navegador.
- Rutas, navegación o seguimiento GPS.
- Integración conversacional y de runtime.

## Compatibilidad

La versión reutiliza `GeoPointSignal` de `core.maps_foundation` y no modifica los
módulos geográficos existentes. Todos los contratos son inmutables, validan sus
invariantes y generan identificadores deterministas.

## Próximo incremento

M325.8 incorporará un adaptador de geocodificación Nominatim detrás de
`MapGeocodingProvider`, con cliente inyectable, timeout, caché y pruebas sin red.
