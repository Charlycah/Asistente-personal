# ROBY XI.2 — R-CAP17-O3-S14 GREEN quirúrgico

## Baseline y alcance

Base: R-CAP17-O3-S13 RED contractual. Se mantienen S11 y los siete contratos S13 sin modificación. La integración se limita a tres autoridades existentes:

- `app/governed_local_library_conversation.py`: bifurcación gobernada de rutas explícitas anidadas frente a búsqueda convencional; sin enumerar catálogo para ruta explícita; etiqueta derivada de la entrada seleccionada.
- `core/governed_local_library/conversation_selection.py`: método de selección explícita en el selector canónico existente.
- `core/governed_local_library/handoff.py`: discriminación entre fingerprint de catálogo y fingerprint de entrada explícita, exactamente uno requerido; revalidación de fingerprint de entrada en recuperación.

No se modifica `app/runtime_ui_adapter.py`, ni el wiring de admisión Knowledge, ni Document Reading, ni Unified Retrieval, ni el límite de catálogo. No se introducen gestores, índices, caches ni autoridades paralelas.

## Semántica

La selección convencional conserva `catalogue_fingerprint`; la selección explícita usa `explicit_entry_fingerprint` sin atribuirse un catálogo no construido. El recuperador sigue revalidando `entry_id` y `source_reference`, y adicionalmente compara el fingerprint explícito cuando corresponde. La solicitud y el paso de recuperación conservan el mismo `query`.

## Certificación local ejecutada

- Contratos S13 + S11 + catálogo original: **27 PASS**.
- EPUB + selección execution-scoped + handoff + S13: **56 PASS**.
- `compileall` sobre los tres archivos modificados: **PASS**.
- Ruff local: **no disponible**; pendiente Windows.

## Certificación Windows pendiente / STOP

No sustituir baseline O2 antes de certificar Windows. Ejecutar Ruff focal, S13, S11, catálogo original y regresiones de handoff. M377 S1–S4 HOLD (47 RED intencionales); E1-B congelado; MODEL_ACQUISITION UNMAPPED/DENY/NO-GO.
