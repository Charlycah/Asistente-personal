# ROBY XI.2 — CAP-17 GREEN quirúrgico

## Execution-Scoped Local Selection → Unified Retrieval Runtime

Baseline oficial de entrada: **13.751 PASS + Ruff limpio**.

Este GREEN implementa únicamente el transporte efímero de una selección local
explícita ya certificada hacia la autoridad existente de ejecución unificada.

Cadena certificada por contrato:

`GovernedLocalDocumentRetrievalRequest → BoundGovernedLocalDocumentRetrieverV1 → execution_retrievers → KnowledgeRetrievalExecutionGateway → OfficialUnifiedRetrievalExecutionRuntimeGateway → KnowledgeRetrievalExecution → STOP`

## Cambios productivos

- `core/governed_local_library/runtime_binding.py`: añade
  `BoundGovernedLocalDocumentRetrieverV1`, ligado a un request y step exactos.
- `core/knowledge_retrieval_execution/gateway.py`: acepta retrievers efímeros por
  ejecución sin persistirlos y rechaza cualquier intento de sobrescribir un
  retriever persistente.
- `app/unified_retrieval_execution_runtime.py`: transporta esos retrievers por
  llamada hacia el gateway canónico conservando snapshot y last_execution.
- `core/governed_local_library/__init__.py`: exporta el binding CAP-17.

## Invariantes preservados

- `KnowledgeRetrievalStep` no cambia de esquema ni de identidad.
- No existe selección implícita por primer resultado.
- El binding falla cerrado ante otro `step_id`, source o query.
- Los retrievers por ejecución no se guardan en el registry persistente.
- No pueden sobrescribir retrievers persistentes, incluidos los externos M260.
- Una ejecución posterior sin binding no reutiliza una selección anterior.
- El resultado continúa siendo el `KnowledgeRetrievalExecution` canónico.
- La provenance `local-library:...` sobrevive hasta el artifact.
- No hay Memory, Learning, persistencia de selección ni mutación de Biblioteca.
- `.roby/config.json` permanece protegido.

## Corrección contractual integrada

Se integró la corrección de imports suministrada por el usuario. Durante la
validación GREEN se detectó además que dos fixtures RED intentaban fabricar un
`KnowledgeRetrievalStep.step_id` inconsistente mediante `dataclasses.replace`.
El modelo canónico ya rechaza correctamente esa identidad antes de alcanzar el
binding. Los fixtures se corrigieron para construir un segundo step legítimo,
con query e identidad canónicas distintas, preservando exactamente el objetivo
del contrato sin debilitar `KnowledgeRetrievalStep`.

## Validación dirigida del asistente

- Contrato de transporte CAP-17: **18 passed**.
- CAP-17 catálogo + handoff + transporte, M171, M174 y M267: **116 passed**.
- Comprobación de `compileall`: limpia.
- Comprobación manual de líneas >88 en archivos tocados: limpia.

La certificación completa (`ruff check .` + `pytest -q`) corresponde al entorno
local oficial del usuario.

## STOP

Este GREEN termina en ejecución unificada del artifact local.

Quedan fuera:
- intención conversacional `biblioteca` / `mis libros`;
- acceso iniciado por usuario o ROBY desde conversación;
- diálogo de desambiguación;
- EPUB;
- Memory/Learning;
- indexación masiva/background.

Siguiente gate recomendado:

**CAP-17 — reconciliación quirúrgica de la capa conversacional Biblioteca:
user-initiated + governed ROBY-initiated + ambiguity handling.**
