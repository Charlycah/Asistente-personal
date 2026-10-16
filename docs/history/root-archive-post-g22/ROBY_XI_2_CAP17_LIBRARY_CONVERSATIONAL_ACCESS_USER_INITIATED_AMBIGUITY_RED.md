# ROBY XI.2 — CAP-17 — RED contractual
## Library Conversational Access — User Initiated + Ambiguity

### Baseline de entrada
- 13.769 PASS + Ruff limpio, certificado localmente.
- Transporte productivo CAP-17 hasta Unified Retrieval Runtime ya GREEN.

### Objetivo
Abrir exclusivamente la capa humana explícita de Biblioteca y la resolución gobernada 0/1/N de candidatos.

### Autoridades preservadas
- `OfficialKnowledgeRuntimeGateway`: clasificación/entrada oficial de necesidad de fuentes.
- `KnowledgeSourcePolicy`: policy canónica de fuentes.
- `KnowledgeRetrievalOrchestrator`: planificación canónica de retrieval.
- `GovernedLocalLibraryCatalogueV1`: catálogo/búsqueda instrumental.
- `GovernedLocalDocumentRetrieverV1`: lectura del documento seleccionado.
- `BoundGovernedLocalDocumentRetrieverV1`: binding one-shot ya certificado.
- `OfficialUnifiedRetrievalExecutionRuntimeGateway`: ejecución unificada oficial.

### Productos esperados para GREEN
El RED espera un producto instrumental en:

`core.governed_local_library.conversation_selection`

con:
- `GovernedLibrarySelectionDisposition`
  - `NO_MATCH`
  - `SELECTED`
  - `NEEDS_DISAMBIGUATION`
- `GovernedLibraryConversationalSelectionV1.decide(search_result)`

Y un adapter de composición en:

`app.governed_local_library_conversation`

con:
- `GovernedLocalLibraryConversationV1`
- `handle_user_request(owner, text, search_query, now)`

El adapter no es una nueva autoridad. Sólo compone authorities existentes.

### Contratos RED
1. `biblioteca` clasifica como `LOCAL_DOCUMENTS`.
2. `mis libros` clasifica como `LOCAL_DOCUMENTS`.
3. Un pedido de Biblioteca que contiene `buscá` no cae en WEB.
4. 0 matches → `NO_MATCH`, sin selección.
5. 1 match → `SELECTED` + `GovernedLibrarySelection` explícita.
6. N matches → `NEEDS_DISAMBIGUATION`, sin selección.
7. N matches nunca usa el primer resultado implícitamente.
8. Los candidatos de desambiguación permanecen bounded.
9. Selección única usa el handoff/binding CAP-17 certificado.
10. La adquisición entra por el Unified Retrieval Runtime existente.
11. Provenance sobrevive hasta el resultado conversacional/artifact.
12. Ambigüedad produce cero lecturas de documentos.
13. No Memory/Learning/admission/persist.
14. `KnowledgeRetrievalStep` no cambia de schema.
15. `.roby/config.json` no cambia.

### STOP
Fuera de este RED:
- iniciativa autónoma de ROBY;
- `GovernedIndependenceAuthorizationBoundaryV1` wiring;
- configuración estable de `D:\Biblioteca`;
- EPUB;
- background indexing/crawling;
- Memory/Learning;
- modificación de libros;
- nuevo router/manager/orchestrator/brain.

### Resultado RED esperado
Los marcadores conversacionales fallan porque todavía no reconocen Biblioteca como fuente local, y los productos `conversation_selection` / `governed_local_library_conversation` todavía no existen.
