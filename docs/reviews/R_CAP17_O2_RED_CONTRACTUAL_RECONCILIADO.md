# ROBY XI.2 — R-CAP17-O2 — RED CONTRACTUAL DE OBSERVABILIDAD Y LATENCIA

Fecha: 2026-10-11. Base inspeccionada: `ultima version corregida(5).zip` (7.581 entradas).

## Autoridades reutilizadas
- `core/governed_local_library/catalogue.py`: `GovernedLocalLibraryCatalogueV1.search` → `catalogue` → `_scan_entries` (os.walk). Recorrido síncrono, límite por entradas, no por duración.
- `app/governed_local_library_conversation.py`: `GovernedLocalLibraryConversationV1.handle_admitted_request` → búsqueda → selección → recuperación por runtime unificado.
- `app/unified_runtime_observability.py` y `core/observability.py`: mecanismos de observabilidad ya existentes. No se crea una autoridad alternativa.
- `app/governed_local_library_runtime_wiring.py`: O1 presente (consultas compuestas y NO_MATCH acotado).

## RED introducido
Archivo **nuevo de pruebas solamente**: `tests/architecture/test_cap17_o2_latency_observability_contract_red.py`.

1. Caracterización de búsqueda de EPUB anidado: PASS.
2. Exigir evidencia de duración diferenciada de escaneo y matching en resultado de búsqueda: RED.
3. Exigir evidencia por solicitud de última etapa completada y tiempos por etapa en resultado conversacional: RED.

Ejecución local: **1 PASS, 2 FAIL esperados**. Regresión O1: **3 PASS**.

Las denominaciones de campos son una propuesta contractual concreta; en el GREEN se debe contrastar con los mecanismos existentes y conservar una sola autoridad de observabilidad. Los campos propuestos por sí solos no demuestran instrumentación ni detectan una operación colgada antes de devolver resultado: un eventual contrato adicional para progreso durante la ejecución requiere revisión de la superficie canónica de diagnóstico, sin estado lateral ni nueva autoridad.

## Protección y límites
- Ningún archivo productivo modificado.
- No se cambió el adaptador protegido, M377, la lectura EPUB, las políticas de raíz, el catálogo ni la recuperación unificada.
- No se ha ejecutado la suite global ni Ruff en este entorno.
- Los 47 RED M377 permanecen bajo HOLD; no se afirma corrección del episodio de cinco minutos.
- STOP antes de GREEN. El Owner debe validar alcance contractual antes de autorizar la implementación.
