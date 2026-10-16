# ROBY XI.2 — CAP-17 RED contractual

## Execution-Scoped Local Selection → Unified Retrieval Runtime

Baseline de entrada: **13.751 PASS + Ruff limpio**.

Este RED congela exclusivamente el transporte productivo de una selección local ya explícita y certificada hacia la autoridad existente de ejecución unificada.

Contrato objetivo:

`GovernedLocalDocumentRetrievalRequest → bound one-shot retriever → execution-scoped retriever → OfficialUnifiedRetrievalExecutionRuntimeGateway → canonical KnowledgeRetrievalExecution → STOP`

El RED exige que el binding acepte sólo el `step_id` exacto al que fue ligado; que la inyección de retrievers sea efímera por ejecución; que no pueda reemplazar un retriever persistente (incluidos los retrievers externos M260); que `last_execution`, `snapshot.evaluations`, artifact canónico y provenance se preserven; y que una ejecución posterior sin binding no pueda reutilizar una selección previa.

## Límites

No se modifica `KnowledgeRetrievalStep`.

No se crea otro orchestrator, execution gateway, runtime root, manager ni autoridad cognitiva.

No se implementa todavía intención conversacional "biblioteca" / "mis libros".

No hay Memory, Learning, indexación en background, selección por `matches[0]` dentro del runtime ni persistencia global de selecciones.

`.roby/config.json` permanece protegido.

## RED esperado

18 fallos contractuales nuevos sobre los 13.751 tests previamente verdes. En la primera apertura del RED, los fallos deben provenir de la ausencia de `core.governed_local_library.runtime_binding`; no de regresiones preexistentes.
