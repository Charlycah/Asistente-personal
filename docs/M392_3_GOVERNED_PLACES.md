# M392.3 — Lugares Gobernados

## Objetivo

Ampliar `internal_world_model` con una representación explícita, inmutable y de sólo lectura de lugares ya resueltos por `location_resolution` y ya aceptados por `places_knowledge`.

## Autoridad

La autoridad canónica continúa siendo `internal_world_model`. `location_resolution` conserva la resolución de referencias y `places_knowledge` conserva el conocimiento del lugar. M392.3 sólo proyecta esas evidencias.

## Reglas

- Sólo se representan perfiles `PlaceKnowledgeProfile` con estado `READY`.
- La ubicación fuente debe estar `RESOLVED`.
- No se crean lugares desde texto libre, GPS en vivo, sensores o inferencias contextuales.
- La representación no expone coordenadas como mecanismo de seguimiento.
- No crea repositorio, persistencia, geocodificador, proveedor, gestor paralelo ni procesos residentes.
- Fuentes no listas o no resueltas permanecen visibles como riesgos de revisión.

## Integración

`InternalWorldModelFoundation.places_representation()` delega en `GovernedPlacesRepresentationView` sin modificar datos fuente.
