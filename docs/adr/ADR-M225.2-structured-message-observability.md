# ADR M225.2 — Structured Message Observability

## Decisión

La consola de desarrollo observa la representación estructurada de `LLMRequest` sin modificarla. El resumen informa el transporte efectivo y los conteos por rol. El contenido solo se revela con `--observe`; las vistas históricas ordinarias continúan sin exponer texto doméstico.

## Consecuencias

- Se puede verificar que el proveedor recibe roles `system`, `user` y `assistant`.
- El fallback de prompt plano permanece observable y compatible.
- No se persisten copias nuevas del contenido ni se altera la inferencia.
