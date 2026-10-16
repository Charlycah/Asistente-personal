# ROBY XI.2 — CAP-17 — GREEN quirúrgico — Cognitive Evidence Need → Local Library Proposal

Base contractual: CAP-17 Cognitive Evidence Need → Local Library Proposal RED, certificada con 13.841 PASS + 19 FAIL intencionales + Ruff limpio.

## Integración

- `OfficialKnowledgeRuntimeGateway` incorpora `assess_evidence_requirement(...)` para evaluar un `DiscriminatingEvidenceRequirement` estructurado sin simular marcadores conversacionales.
- `GovernedCognitiveEvidenceToLocalLibraryBridgeV1` traduce una necesidad epistemológica ya producida por `governed_reasoning` a una decisión mediante `KnowledgeSourcePolicy`.
- El bridge sólo propone Biblioteca cuando la autoridad canónica devuelve `LOCAL_SOURCE_PREFERRED`; no busca ni lee archivos directamente.
- La propuesta preserva `requirement_id`, `source_reference`, `world_snapshot_id` y `source_decision_id`.
- La iniciativa sigue pasando por `GovernedRobyInitiatedLibraryAccessV1` y `GovernedIndependenceAuthorizationBoundaryV1`.
- `GovernedLocalLibraryConversationV1.handle_admitted_request(...)` es la convergencia neutral compartida después de la admisión; el camino ROBY-initiated deja de fingir una petición humana.
- Productive Runtime Wiring expone el bridge únicamente cuando la Biblioteca está provisionada.

## Autoridades preservadas

No se añade planner, agente, reasoning owner, knowledge runtime, source policy, library reader ni retrieval runtime alternativo. `KnowledgeRetrievalStep` conserva su esquema histórico. El bridge no introduce Memory/Learning, procesos background, raíces hardcodeadas ni acceso directo al filesystem.

## STOP

El corte termina en la propuesta y, si es autorizada, reutiliza la cadena CAP-17 existente de selección 0/1/N → DocumentReadingService → Unified Retrieval Runtime. No se crea adquisición genérica automática ni aprendizaje.
