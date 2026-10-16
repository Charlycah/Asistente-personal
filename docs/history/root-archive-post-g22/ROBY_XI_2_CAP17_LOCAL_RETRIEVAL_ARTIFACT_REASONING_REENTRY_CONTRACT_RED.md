# ROBY XI.2 — CAP-17
## Local Retrieval Artifact → Governed Reasoning Re-entry — RED contractual

### Base oficial

`ROBY_XI_2_CAP17_PRODUCTIVE_REASONING_LIBRARY_BRIDGE_INVOCATION_GREEN_M249_FIX.zip`

Certificación de entrada: **13.881 PASS + Ruff limpio + 0 FAIL**.

### Propósito

Cerrar únicamente el retorno de una evidencia local **ya adquirida** por CAP-17 hacia la autoridad canónica `governed_reasoning`, sin repetir búsqueda, selección, lectura o retrieval y sin registrar todavía la adquisición dentro del episodio CAP-11.

### Autoridad y componente permitido

Se permite un único adaptador instrumental:

`app.governed_local_evidence_reasoning_reentry.GovernedLocalEvidenceReasoningReentryV1`

No es Reasoner, Planner, Manager, Router, Agent ni Orchestrator. Su única función contractual es proyectar un resultado CAP-17 completado a `EvidenceReference`, registrarlo mediante el `evidence_registry` ya poseído por `governed_reasoning` y solicitar exactamente una reevaluación al `OfficialGovernedReasoningRuntimeGateway`.

### Contrato de entrada

La entrada debe conservar la lineage cognitiva original:

- owner;
- turn_id;
- originating_reasoning_id;
- `DiscriminatingEvidenceRequirement` original;
- episode_id ya abierto;
- resultado CAP-17 existente.

El `requirement_id`, `source_reference` y `world_snapshot_id` válidos son los del `DiscriminatingEvidenceRequirement` original. Se prohíbe sustituirlos por los identificadores auxiliares `*-direct-*` generados por la autorización de iniciativa de Biblioteca.

### Elegibilidad

Sólo es elegible una cadena realmente completada:

`LOCAL_LIBRARY_PROPOSED -> ROBY initiated COMPLETED -> library conversation COMPLETED -> KnowledgeRetrievalExecution existente -> KnowledgeRetrievalArtifact existente -> LOCAL_DOCUMENTS`.

Cualquier 0-match, ambiguity, MUST_ASK, ABSTAINED, REVIEW_REQUIRED, FAILED, unavailable, artifact ausente, execution ausente o mismatch de lineage debe cerrar en fail-closed sin registrar evidencia y sin invocar reasoning.

### Proyección de evidencia

La evidencia debe registrarse como:

- `EvidenceSourceType.KNOWLEDGE`;
- `EvidenceKind.OBSERVATION`;
- `EvidenceSensitivity.PERSONAL`;
- `epistemic_role=local_document_evidence_not_truth`.

La metadata debe conservar como mínimo:

- knowledge_source=local_documents;
- originating_reasoning_id;
- requirement_id original;
- episode_id;
- source_decision_id;
- knowledge_execution_id;
- selected_source_reference;
- world_snapshot_id.

El summary debe ser bounded. El fingerprint debe ser determinista y depender de la ejecución Knowledge, el artifact y la fuente local seleccionada.

### Reentrada

Después de registrar exactamente una referencia, el adaptador debe invocar exactamente una vez `reasoning_gateway.reason(...)` con un `ReasoningQuery` que incluya exclusivamente el nuevo `evidence_id` como evidencia explícita.

La reentrada no establece verdad. No crea Memory, Learning, world-model, preguntas, planificación, nuevas adquisiciones ni background work.

### Idempotencia

Una misma `KnowledgeRetrievalExecution.execution_id` no puede provocar dos reevaluaciones. La segunda entrada debe resultar `already_consumed`.

### Integración productiva

El contributor productivo CAP-17 ya existente debe encadenar el resultado completado al nuevo adaptador, y `runtime_root_factory.py` debe componer el adaptador usando el `governed_reasoning_runtime` ya existente. No se crea un runtime u orquestador nuevo.

### STOP explícito

Este bloque termina después de la reevaluación de `governed_reasoning`.

**No** se modifica todavía `GovernedMultiStepInvestigationEpisodeBoundaryV1`, no se registra aún esta procedencia en el episodio CAP-11 y no se dispara continuación long-horizon.

### Invariantes

- `KnowledgeRetrievalStep` permanece intacto.
- `GovernedAcquiredEvidenceEnvelope` permanece reservado al carril Level-2/`OfficialCapabilityGateway`.
- No hay segunda retrieval.
- No hay modificación de EPUB, catalogue, 0/1/N o selección.
- No hay Memory/Learning/background.
- `.roby/config.json` no se modifica.
