# ROBY XI.2 — CAP-17 RED contractual

## Governed Local Library Catalogue Foundation

Baseline de entrada: `13.722 PASS + Ruff limpio`.

Este RED congela únicamente la frontera Foundation de Biblioteca Personal:

- raíz explícitamente inyectada y autorizada;
- catálogo metadata-first, read-only y bounded;
- containment estricto;
- identidad determinista y provenance;
- búsqueda determinista y bounded;
- sin lectura masiva de contenido;
- sin Memory/Learning;
- sin background crawler;
- sin modificación de `.roby/config.json`.

La raíz real de despliegue es `D:\\Biblioteca`, pero el contrato usa `tmp_path`:
la ubicación real no se hardcodea en producción.

El RED debe fallar exclusivamente porque todavía no existe el módulo productivo
`core.governed_local_library` / su API contractual.

STOP: antes de lectura semántica, Knowledge admission, Memory y Learning.
