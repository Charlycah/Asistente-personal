# ROBY XI.2 — CAP-17 — GREEN quirúrgico — EPUB Library Reading Support

Base de entrada: RED EPUB certificado con **13.826 PASS + Ruff limpio + 14 fallos intencionales EPUB**.

## Integración

EPUB se integra exclusivamente en la autoridad existente `DocumentReadingService` y en el catálogo gobernado `GovernedLocalLibraryConfig`. No se crea reader, manager, runtime, router, planner ni autoridad adicional.

`DocumentReadingService` abre el contenedor EPUB en memoria con `zipfile`, resuelve `META-INF/container.xml`, localiza el paquete OPF, sigue `manifest` + `spine` en orden de lectura y convierte únicamente los recursos referenciados por el spine a texto legible. No extrae miembros al filesystem.

## Límites gobernados

- Máximo: 512 miembros ZIP.
- Máximo: 8.000.000 bytes descomprimidos acumulados.
- Se rechazan rutas internas absolutas o con traversal.
- EPUB corrupto, container/OPF/spine/recurso requerido ausente o XML inválido falla con error EPUB gobernado.
- Se conserva `_MAX_BYTES` para el archivo contenedor y `_MAX_CHARS` para el texto final.
- No hay DRM circumvention, OCR, embeddings, indexación global, Memory/Learning ni scanning/background.

## Integración CAP-17

`.epub` pasa a formar parte de los sufijos por defecto de `GovernedLocalLibraryConfig`. La selección explícita, handoff, bound retriever y Unified Retrieval Runtime existentes permanecen sin cambios y producen el mismo `KnowledgeRetrievalArtifact` canónico.

El contrato histórico de formato no soportado conserva su semántica usando `.mobi` como ejemplo.

## Invariantes preservadas

`KnowledgeRetrievalStep`, `app/governed_local_library_runtime_wiring.py`, `app/runtime_root_factory.py` y `.roby/config.json` permanecen fuera de esta modificación. EPUB no se introduce en Productive Runtime Wiring.

## STOP

El bloque termina en EPUB → `DocumentReadingService` → handoff existente → `KnowledgeRetrievalArtifact`.
