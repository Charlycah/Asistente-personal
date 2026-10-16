# R-CAP17-O3-S13 — RED contractual quirúrgico de integración conversacional

## Baseline y alcance

Baseline: R-CAP17-O3-S11 GREEN quirúrgico (20/20 focal Windows, Ruff PASS), sin reemplazar el baseline O2 certificado. Solo se incorpora el test contractual S13 y este documento; **sin modificaciones productivas**.

## Causa observada

S7 demostró catálogo limitado a 10.000 entradas, 10.001 examinadas, copia raíz incluida y EPUB anidado excluido. S11 introdujo y certificó `lookup_explicit_relative_path()` dentro de la autoridad canónica, sin conectar el flujo conversacional.

## RED requerido

- La solicitud de biblioteca admitida que contiene una ruta relativa explícita debe alcanzar el archivo anidado fuera del catálogo truncado.
- La ruta explícita no debe llamar a `_scan_entries()` ni reconstruir el catálogo.
- La selección debe conservar identidad, procedencia real y etiqueta segura; **no fabricar un fingerprint de catálogo inexistente**.
- La recuperación debe seguir usando el Unified Retrieval Runtime y el recuperador canónico, con revalidación antes de leer.
- Las rutas inválidas deben fallar cerradas y no producir lecturas.
- Las solicitudes no admitidas por Knowledge no deben producir lecturas.
- La extracción de una ruta citada entre comillas debe conservar su texto.

## Restricciones de diseño antes de GREEN

La interfaz `GovernedLibrarySelection` hoy exige `catalogue_fingerprint`. Cualquier solución deberá resolver semánticamente ese contrato sin simular un catálogo; deberá preservar el selector único, la igualdad `step.query == selection.query`, el origen de `safe_source_label` y la instrumentación O2. El RED no aprueba una forma de implementación ni modifica la API de selección. No introducir segundo buscador, runtime, lector, índice, caché o escaneo de fondo.

## Certificación

Ejecutar Ruff y el pytest focal S13 en Windows. Los fallos por la falta de integración conversacional son intencionales. Conservar O2 GREEN, M377 S1-S4 HOLD (47 RED intencionales), adaptador protegido, E1-B congelado y MODEL_ACQUISITION NO-GO. STOP antes de GREEN.
