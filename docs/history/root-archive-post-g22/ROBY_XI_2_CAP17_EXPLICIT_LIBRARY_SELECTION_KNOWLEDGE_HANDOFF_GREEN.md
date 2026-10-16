# ROBY XI.2 — CAP-17 GREEN quirúrgico del handoff aislado

## Explicit Library Selection → Document Reading → Knowledge Artifact

Baseline de entrada certificada por el usuario: `13.734 PASS + Ruff limpio`.

Este GREEN implementa únicamente el handoff aislado fijado por el RED contractual:

`Library search → explicit selection → resolve_entry → existing document reader → KnowledgeRetrievalArtifact(LOCAL_DOCUMENTS) → STOP`

Cambios productivos:

- `core/governed_local_library/handoff.py`
- exports públicos mínimos en `core/governed_local_library/__init__.py`

Contratos incorporados:

- selección explícita con `entry_id`, `source_reference` y `catalogue_fingerprint`;
- rechazo de selección desconocida, stale o con provenance inconsistente;
- conservación exacta de la query del `KnowledgeRetrievalStep`;
- delegación de lectura mediante el reader existente, sin duplicar lectura documental;
- producción del `KnowledgeRetrievalArtifact` canónico con `LOCAL_DOCUMENTS`;
- ninguna mutación de Biblioteca;
- ninguna acción de Memory/Learning;
- formatos y tamaño continúan gobernados por `DocumentReadingService`;
- no existe `retrieve(step)`: no hay selección implícita ni wiring prematuro al runtime.

No se modifican `KnowledgeRetrievalStep`, `KnowledgeRetrievalExecutionGateway`,
`OfficialUnifiedRetrievalExecutionRuntimeGateway`, `app/runtime_root_factory.py` ni
`.roby/config.json`.

La raíz real `D:\Biblioteca` continúa siendo configuración de despliegue y no se
hardcodea.

Validación dirigida del candidato GREEN en entorno del asistente:

- 17 contratos del handoff: PASS;
- 12 contratos CAP-17 Foundation: PASS;
- foundations M340.4/M169/M170/M171/M251/M267: PASS;
- total dirigido: `127 passed`;
- `compileall`: limpio;
- no se detectaron líneas nuevas > 88 caracteres.

La certificación oficial completa requiere `ruff check .` y `pytest -q` en el entorno
local del usuario.
