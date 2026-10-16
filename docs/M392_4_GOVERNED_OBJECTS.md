# M392.4 — Objetos Gobernados

M392.4 amplía `InternalWorldModelFoundation` con una vista inmutable de objetos ya consolidados por `object_knowledge`.

## Autoridad

La autoridad canónica continúa siendo `internal_world_model`. `object_knowledge` conserva la consolidación de evidencia de objetos. M392.4 no crea un gestor, repositorio ni detector paralelo.

## Contrato

- Sólo proyecta `ObjectKnowledgeProfile` con estado `AVAILABLE` y conocimiento declarado.
- Conserva trazabilidad hacia `profile_id`, `object_ref` y `evidence_refs`.
- No crea inventario automático, detección, tracking, OCR, búsqueda de productos ni biometría.
- No infiere propietario ni ubicación del objeto.
- No añade persistencia, automatización, autoridad ni cambios de runtime.
- La salida es determinista, ordenada, inmutable y de solo lectura.
