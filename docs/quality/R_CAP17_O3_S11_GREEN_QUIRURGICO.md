# R-CAP17-O3-S11 — GREEN quirúrgico

## Alcance
Se implementa `GovernedLocalLibraryCatalogueV1.lookup_explicit_relative_path()` en la autoridad canónica existente, sin conexión conversacional.

## Restricciones
- Ruta relativa anidada explícita, separadores POSIX, sin componentes vacíos, `.` ni `..`.
- Extensión permitida por configuración existente.
- Sin escape de raíz autorizada ni symlinks intermedios cuando `follow_symlinks=False`.
- Reutiliza `resolve_entry`, `_entry_from_path` y `validate_selected_entry` para identidad/procedencia y revalidación.
- No invoca `_scan_entries` ni introduce índice/caché/autoridad paralela.

## Certificación local
`python -m pytest -q tests/architecture/test_cap17_o3_explicit_relative_path_contract_red.py`: 8 passed in 0.40s.
Ruff: no disponible en el entorno local; requiere Windows.
Suite integral: no ejecutada. Certificación Windows: pendiente.

## Límites
No modifica wiring conversacional, Unified Retrieval, DocumentReadingService ni runtime_ui_adapter.py. No resuelve búsquedas temáticas fuera del catálogo truncado. No se certifica latencia conversacional.

## Gobernanza
O2 GREEN se mantiene como baseline; M377 HOLD, E1-B congelado, MODEL_ACQUISITION NO-GO. STOP pendiente de certificación Windows.
