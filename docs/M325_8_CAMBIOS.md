# ROBY XI.2 — M325.8

## Nominatim Geocoding Adapter

Se agregó `infrastructure/maps/nominatim_geocoding.py` con:

- `NominatimGeocodingConfig`
- `NominatimGeocodingAdapter`
- errores normalizados de proveedor
- caché TTL en memoria
- control de intervalo mínimo
- transporte HTTP de biblioteca estándar

Se agregaron 30 pruebas en:

`tests/test_m325_8_nominatim_geocoding_adapter.py`

Resultado de la suite en el entorno de construcción:

`7262 passed`

Ruff debe confirmarse en el entorno local del proyecto.
