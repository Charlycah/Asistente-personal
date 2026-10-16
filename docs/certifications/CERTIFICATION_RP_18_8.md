# Certificación RP.18.8 — Ejecución única

RP.18.8 certifica que la ejecución operacional normal de ROBY converge en una sola
cadena oficial:

`main:main` → `build_official_runtime_from_environment()` →
`OfficialROBYRuntime` → gateway conversacional → registro y gateway de capacidades.

## Garantías

- Existe un único punto de entrada canónico de proceso.
- Existe una única autoridad canónica de lifecycle: `OfficialROBYRuntime`.
- Consola y escritorio usan esa misma autoridad.
- Los residentes se anexan al runtime oficial y no arrancan por una segunda vía.
- Las superficies de compatibilidad no son ejecutables como roots oficiales.
- Conversation, bootstrap y composition root conservan identidad de objeto.
- Observabilidad, readiness y recuperación leen el mismo grafo operacional.

`--no-lifecycle` se conserva como modo explícito de desarrollo y diagnóstico; no se
considera una ejecución operacional certificada de larga vida.
