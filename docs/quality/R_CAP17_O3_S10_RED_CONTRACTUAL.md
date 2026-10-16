# R-CAP17-O3-S10 — RED contractual quirúrgico (propuesta)

## Estado
RED propuesto, sin cambios productivos. STOP antes de GREEN. No modifica M377.

## Evidencia
S5: 0 matches, bounded=True, 16.237 s. S6: matching por ruta relativa PASS con catálogo completo y truncado. S7: 10.000 entradas catalogadas, 10.001 examinadas; archivo raíz presente y anidado ausente.

## Contrato propuesto
Extender **solo** `GovernedLocalLibraryCatalogueV1` con `lookup_explicit_relative_path(relative_path)` para rutas **relativas explícitas y anidadas**, devolviendo una `GovernedLibraryEntry` canónica, sin enumerar el catálogo. Rechazar consultas por nombre simple, rutas vacías/absolutas, escapes, extensiones no admitidas, archivos no regulares y enlaces simbólicos en cualquier componente si `follow_symlinks=False`. Mantener `validate_selected_entry` como revalidación previa a la lectura.

## Límite de alcance
Los tests de este paquete caracterizan la primitiva de catálogo. **No certifican** admisión conversacional, fingerprint de selección, integración con Knowledge/Unified Retrieval ni observabilidad. Esos contratos deben reconciliarse antes de autorizar GREEN; no debe fingirse un fingerprint de catálogo no construido. Las búsquedas temáticas siguen limitadas. No índice, caché, background scan ni autoridad paralela.

## RED esperado
`AttributeError` por ausencia de `lookup_explicit_relative_path` en el baseline O2. Esto es un fallo intencional del contrato propuesto, no una regresión productiva.

## Gate
Certificar RED local y revisar cobertura de contratos de integración antes de autorizar implementación. Conservar Ruff, E501, imports ordenados, O1/O2 y M377 HOLD.
