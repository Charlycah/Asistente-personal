# ROBY XI.2 — CAP-17 RED contractual

## Explicit Library Selection → Document Reading → Knowledge Artifact

Baseline oficial de entrada: `13.734 PASS + Ruff limpio`.

Este RED abre únicamente el residual identificado tras CAP-17 Foundation:
representar una selección explícita de una entrada de Biblioteca y adquirir ese
único documento mediante `DocumentReadingService`, devolviendo el artefacto
canónico `KnowledgeRetrievalArtifact` con fuente `LOCAL_DOCUMENTS`.

El contrato NO registra todavía un retriever en el runtime general. Tampoco
extiende `KnowledgeRetrievalStep`, no crea otro orchestrator y no selecciona el
primer resultado implícitamente.

API contractual esperada en el GREEN:

- `GovernedLibrarySelection`
- `GovernedLocalDocumentRetrievalRequest`
- `GovernedLocalDocumentRetrieverV1`
- `retrieve_selected(request)`

Invariantes:

- selección explícita por `entry_id`;
- query de selección = query del `KnowledgeRetrievalStep`;
- fingerprint de catálogo vigente;
- `source_reference` exacto;
- resolución siempre a través del owner CAP-17;
- lectura exclusivamente mediante `DocumentReadingService`;
- salida exactamente `KnowledgeRetrievalArtifact`;
- fuente exactamente `KnowledgeSourceKind.LOCAL_DOCUMENTS`;
- provenance conservada en `references`;
- ningún método `retrieve(step)` todavía, para impedir wiring prematuro y
  selección implícita;
- cero Memory/Learning;
- cero mutación de Biblioteca;
- `.roby/config.json` intacto;
- EPUB continúa sin soporte de lectura productivo;
- límite de 2 MB continúa bajo `DocumentReadingService`.

STOP del incremento:

`explicit selection → resolve_entry → DocumentReadingService → Knowledge artifact`

Nada posterior a ese artefacto pertenece a este GREEN.
