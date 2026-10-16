# ROBY XI.2 — R-CAP17-O1 — RED CONTRACTUAL

## Alcance y evidencia

Base: `ultima version corregida(4).zip`. El Owner observó: (1) consulta compuesta mal delimitada; (2) consulta por nombre de carpeta sin coincidencias; (3) consulta por nombre exacto EPUB sin respuesta visible tras cinco minutos, sin error de consola y con cierre normal por «Salir».

## Autoridades reutilizadas

- `core/governed_local_library/catalogue.py`: catálogo y búsqueda bounded; recursividad existente.
- `core/governed_local_library/models.py`: EPUB admitido; bandera `bounded` disponible.
- `core/governed_local_library/conversation_selection.py`: selección 0/1/N, preserva `bounded`.
- `app/governed_local_library_conversation.py`: conversación y traspaso a lectura gobernada.
- `app/governed_local_library_runtime_wiring.py`: extracción de consulta y presentación oficial.
- `app/document_reading.py`: lectura de documentos; sin cambios.

## Pruebas nuevas, solo tests

`tests/architecture/test_cap17_o1_runtime_search_contract_red.py`

1. `test_cap17_o1_nested_epub_exact_name_is_searchable`: **PASS**, prueba de reutilización: un EPUB dentro de `Robots e Imperio (15050)` se encuentra tanto por carpeta como por nombre completo. No demanda un módulo de búsqueda nuevo.
2. `test_cap17_o1_truncated_no_match_is_not_reported_as_exhaustive`: **RED contractual**: con catálogo truncado y sin coincidencia, la respuesta oficial no debe afirmar ausencia definitiva; debe advertir que la búsqueda es incompleta o limitada. La bandera `bounded` ya llega al resultado conversacional, pero la presentación actual no la considera.
3. `test_cap17_o1_compound_query_keeps_book_title_only`: **RED contractual**: la consulta observada sobre `el documento Robots e Imperio y decime...` debe separar el título de la instrucción complementaria; no debe buscar el enunciado completo como nombre de archivo.

Ejecución local: `1 passed, 2 failed` (fallas en las aserciones esperadas; no errores de importación). La sintaxis se verificó con `compileall`. Ruff no está instalado en el entorno de ejecución de este análisis; el Owner deberá verificar Ruff en su entorno oficial.

## No demostrado / fuera de este RED

- No está demostrado que `D:\Biblioteca` alcance el límite de 10.000 entradas.
- No está demostrada la causa de los cinco minutos sin respuesta; no se introducen tests con umbrales arbitrarios de rendimiento ni mecanismos de timeout no acordados.
- No se prueba la lectura real del EPUB del Owner, ni se modifica la Biblioteca.
- Noticias deportivas programadas: fuera de alcance.
- No se altera M377 S1–S4 HOLD, E1-B, MODEL_ACQUISITION, UI protegida, ni código productivo.

## STOP

RED local contractual reproducido. No GREEN. Próxima autorización separada: `R-CAP17-O1 — GREEN QUIRÚRGICO`, solo después de certificación local y validación de los límites del contrato.
