# ROBY XI.2 — R-CAP17-O1 GREEN quirúrgico — validación focalizada

## Alcance autorizado
Dos RED contractuales: extracción del título de consulta compuesta y respuesta no definitiva ante búsqueda truncada. Sin cambios en catálogo, lector EPUB, arquitectura ni adaptador protegido.

## Único archivo productivo modificado
`app/governed_local_library_runtime_wiring.py`.
- Interceptor NO_MATCH + bounded: mensaje explícito de búsqueda incompleta, sin afirmar ausencia definitiva.
- `_search_query`: conserva título de documento/libro en solicitudes compuestas `... y decime ...`.

## Evidencia local
- `python -m pytest -q tests/architecture/test_cap17_o1_runtime_search_contract_red.py`: 3 passed.
- `python -m pytest -q tests/architecture/*cap17*`: 235 passed en 3.22 s.
- Ruff no disponible en este entorno; ejecutar Ruff en el entorno Owner.
- Suite global NO ejecutada aquí; los 47 M377 intencionales continúan en HOLD y fuera de alcance.
- No se ha verificado el tiempo de respuesta sobre la Biblioteca real ni la causa de los cinco minutos sin respuesta.

## Integración
Este ZIP es un parche reducido de validación, NO reemplaza el ZIP completo certificado.
Copiar el único archivo productivo al mismo path de la base RED contractual; mantener el test contractual. No integrar sobre una base distinta sin cotejo previo.

## STOP
GREEN focalizado local; pendiente Ruff y suite global del Owner, y certificación de integración sobre ZIP completo.
