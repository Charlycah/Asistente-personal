# Post-M409.1 — Explicit Deliberation Productive Advisory Wiring v1

## Estado de implementación

**IMPLEMENTED / CERTIFICATION PENDING USER GATES**

## Objetivo

Cerrar el primer camino productivo, explícito y gobernado desde alternativas humanas
escritas en el turno actual hasta un advisory M391.6 presentado por la frontera
conversacional oficial.

## Flujo implementado

`OfficialConversationGateway.submit()` conserva precedencia de identificación. Cuando el
turno no fue consumido por identificación, no contiene `external_evidence` y el Producer v1
certifica deliberación `EXPLICIT`, la cadena ejecuta:

`Evidence Producer v1 -> Decision Option Adapter v1 -> CanonicalDecisionFacade.advise() ->
DecisionAdvisoryConversationalRealizer -> LocalConversationTurn(interceptor)`.

Los estados no explícitos, ambiguos o insuficientes conservan el runtime conversacional
previo. La presencia de `external_evidence` también fuerza fallback v1 al runtime normal.

## Realización conversacional

`DecisionAdvisoryConversationalRealizer` es determinista, read-only y sin LLM. No vuelve a
parsear el turno, no rankea, no genera razones ni opciones y no modifica scores. Usa sólo la
estructura del `GovernedDecisionAdvisoryReport`, la evidence certificada y los bindings del
adapter. Toda respuesta preserva expresamente la decisión humana.

## Límites gobernados

- no binding nuevo de `CanonicalDecisionFacade`;
- no modificación de `UnifiedCognitiveCoordinator`;
- no modificación de M391.6;
- Producer v1 y Adapter v1 permanecen FROZEN;
- no M391.5 enrichment;
- no LLM, provider, retrieval o networking en el interceptor;
- no persistence propia del advisory;
- no Initiative, Proactive Care, plan, task ni ejecución;
- M409.1/Residential permanece FROZEN;
- M410/networking permanece NO-GO.

## Validación local disponible

Los tests nuevos de realization + wiring pasan 19/19. El conjunto focal de preservación
incluyendo identificación, conversation entry evidence, unified coordination evidence,
text perception, post-turn reflection, Canonical Decision Facade, Producer v1 y Adapter v1
pasa 125/125.

La certificación final requiere `ruff check .` y `pytest -q` completos sobre el árbol del
usuario, seguidos de Closure Audit.
