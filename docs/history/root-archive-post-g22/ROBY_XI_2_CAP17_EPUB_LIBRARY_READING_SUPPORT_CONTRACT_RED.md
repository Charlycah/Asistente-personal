# ROBY XI.2 — CAP-17 — RED contractual — EPUB Library Reading Support

Base certificada de entrada: **13.826 PASS + Ruff limpio**.

## Propósito contractual

Abrir de forma explícita la migración de EPUB sin cambiar todavía producción. EPUB se incorpora exclusivamente como formato de `DocumentReadingService` y como sufijo permitido por `GovernedLocalLibraryConfig`; no crea una nueva autoridad.

## Contratos RED

El GREEN deberá hacer que un EPUB mínimo válido sea legible, respetar el orden OPF/spine, convertir XHTML/HTML a texto, ignorar recursos fuera del spine, incluir `.epub` en el catálogo por defecto y atravesar la selección explícita/handoff existente hasta producir `KnowledgeRetrievalArtifact`.

El lector deberá fallar gobernadamente ante EPUB corrupto, `container.xml`/spine ausentes y rutas con traversal, sin extraer miembros al filesystem y conservando el límite final de caracteres. El contrato fija además un máximo de **512 miembros ZIP** y **8.000.000 bytes descomprimidos acumulados** para la lectura EPUB. No se permite DRM circumvention, OCR, indexación global, embeddings, Memory/Learning, background scanning ni un nuevo reader/manager/runtime/router.

## Migración histórica explícita

El contrato histórico que usaba `.epub` como ejemplo de formato no soportado se migra a `.mobi`. Así se conserva el contrato general de formato no compatible mientras EPUB deja de estar definido como necesariamente inválido.

## Invariantes

`KnowledgeRetrievalStep` no cambia. `app/governed_local_library_runtime_wiring.py` y `app/runtime_root_factory.py` no cambian. El guardrail que mantiene `.epub` fuera del wiring productivo sigue vigente. `.roby/config.json` no se modifica.

## STOP

El bloque termina en EPUB → `DocumentReadingService` → handoff existente → `KnowledgeRetrievalArtifact`. El productive ROBY proposal source queda fuera de alcance.
