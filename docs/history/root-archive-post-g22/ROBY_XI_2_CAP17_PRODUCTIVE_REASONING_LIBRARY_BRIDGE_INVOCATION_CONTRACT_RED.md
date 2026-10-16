# ROBY XI.2 — CAP-17
## Productive Reasoning Requirement → Cognitive Library Bridge Invocation
### Contract RED

**Base oficial:** `ROBY_XI_2_CAP17_COGNITIVE_EVIDENCE_LOCAL_LIBRARY_PROPOSAL_GREEN_CORREGIDO_FINAL.zip`  
**Baseline certificada por usuario:** 13.860 PASS · Ruff limpio · 0 FAIL.  
**Estado de este paquete:** RED contractual; no implementación de producción autorizada en este ZIP.

## 1. Gap contractual

CAP-17 ya posee un `GovernedCognitiveEvidenceToLocalLibraryBridgeV1` productivamente
provisionado. El residual es exclusivamente de reachability: el ciclo cognitivo ordinario
no consume todavía el `DiscriminatingEvidenceRequirement` exacto admitido por el re-entry
y, por tanto, nunca invoca el bridge desde una necesidad cognitiva productiva real.

## 2. Autoridades que se preservan

- `governed_reasoning` sigue siendo autoridad del episodio, discriminación y requisito.
- `GovernedExplanatoryModelInvestigationReentryV1` sigue siendo boundary read-only de admisión.
- `KnowledgeSourcePolicy` sigue siendo autoridad de selección de fuente.
- `GovernedIndependenceAuthorizationBoundaryV1` sigue siendo autoridad de iniciativa.
- CAP-17 conserva catálogo 0/1/N, `DocumentReadingService` y Unified Retrieval Runtime.
- `CognitiveRuntimeOrchestrator` sigue siendo el único orquestador cognitivo.

No se autoriza un nuevo planner, manager, router, agent, reasoning owner ni loop.

## 3. Adaptador instrumental esperado

Se contractualiza un único contributor del runtime:

`app.productive_reasoning_local_library_bridge_invocation`

con la superficie:

- `GovernedProductiveReasoningLibraryBridgeContributorV1`
- `GovernedProductiveReasoningLibraryInvocationStatus`
- `GovernedProductiveReasoningLibraryInvocationResult`

El contributor es composición instrumental, no autoridad. Debe ser compatible con el
puerto existente `CognitiveRuntimeContributor` y usar el stage
`local_library_evidence`.

## 4. Lineage y turno exactos

Para cada invocación ordinaria el contributor deberá:

1. derivar la identidad con `build_governed_conversation_turn_identity`;
2. recuperar el `CanonicalProductiveReasoningEpisode` del mismo owner/session/turn;
3. recuperar el `GovernedExplanatoryModelInvestigationReentry` del mismo turno;
4. continuar sólo si el re-entry está `ADMITTED`;
5. exigir `reentry.originating_reasoning_id == episode.result.result_id`;
6. reutilizar exactamente `reentry.requirement`;
7. usar como `internal_confidence` exactamente
   `episode.result.decision.confidence_score`.

Está prohibido hardcodear una confianza para favorecer Biblioteca.

## 5. Provisioning y fail-closed

La disponibilidad de Biblioteca se deriva exclusivamente del wiring productivo:

- status `PROVISIONED`;
- `cognitive_bridge` presente.

Si no existe episodio, no existe re-entry, el re-entry no está admitido, el lineage no
coincide o Biblioteca no está provisionada, no se invoca el bridge.

Estados contractuales del contributor:

- `invoked`
- `library_unavailable`
- `no_reasoning_episode`
- `no_investigation_reentry`
- `not_admitted`
- `lineage_mismatch`

## 6. Única ejecución

Una vez satisfechos los gates, el contributor construye
`GovernedCognitiveEvidenceLibraryRequest` con el requisito exacto y delega una sola vez
en `cognitive_bridge.handle(...)`.

El contributor NO puede:

- llamar `library.search`;
- leer archivos;
- usar `DocumentReadingService`;
- seleccionar candidatos;
- llamar directamente `handle_admitted_request`;
- autorizar iniciativa;
- decidir la fuente por fuera del bridge existente.

## 7. Composición productiva

`app/runtime_root_factory.py` debe construir el contributor después del wiring CAP-17 y
componerlo dentro del `CognitiveRuntimeOrchestrator` existente. Se permite reutilizar el
mecanismo ya soportado de `RuntimeCompositionDependencies.cognitive_runtime`; no se crea
un orquestador específico de Biblioteca.

La composición debe ser fail-closed cuando CAP-17 no esté provisionado.

## 8. STOP del bloque

El incremento termina tras obtener el resultado CAP-17 y exponer lineage/referencias
transitorias al mismo turno. Este bloque NO autoriza:

- reinyectar el contenido local en CAP-11;
- replanificar investigación long-horizon;
- Memory;
- Learning;
- persistencia;
- background scanning;
- embeddings/indexación global;
- cambios de `KnowledgeRetrievalStep`;
- cambios de `.roby/config.json`;
- hardcode de `D:\\Biblioteca`.

## 9. Evidencia RED esperada

El archivo
`tests/architecture/test_cap17_productive_reasoning_library_bridge_invocation_red.py`
abre los contratos faltantes y mantiene guardrails verdes sobre schemas/boundaries ya
certificados. La implementación de producción debe permanecer ausente en este RED.
