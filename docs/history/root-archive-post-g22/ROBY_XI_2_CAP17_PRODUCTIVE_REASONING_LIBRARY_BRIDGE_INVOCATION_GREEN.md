# ROBY XI.2 — CAP-17
## Productive Reasoning Requirement → Cognitive Library Bridge Invocation
### GREEN quirúrgico

Base certificada de entrada: 13.860 PASS, Ruff limpio, 0 FAIL.
RED certificado por usuario: 13.863 PASS, 18 FAIL intencionales, Ruff limpio.

## Integración realizada

Se incorporó un único contributor instrumental:
`app.productive_reasoning_local_library_bridge_invocation`.

El contributor se integra al `CognitiveRuntimeOrchestrator` existente y preserva las
autoridades canónicas. Deriva el `turn_id` mediante la identidad gobernada del turno,
recupera el episodio productivo exacto y el re-entry explicativo del mismo turno, exige
admisión y lineage exacto, reutiliza el `DiscriminatingEvidenceRequirement` admitido y
usa exclusivamente `episode.result.decision.confidence_score` como confianza interna.

La disponibilidad de Biblioteca se obtiene del wiring CAP-17 existente. Sólo cuando el
wiring está `PROVISIONED` y existe `cognitive_bridge` se delega una vez en
`GovernedCognitiveEvidenceToLocalLibraryBridgeV1`.

## Límites preservados

No se añadió planner, manager, router, agent ni segundo orquestador. El contributor no
busca archivos, no lee documentos, no selecciona candidatos, no autoriza iniciativa y
no decide fuentes. No cambia `KnowledgeRetrievalStep`, no modifica `.roby/config.json`
y no introduce procesos persistentes o ejecución fuera del turno.

Este bloque termina tras obtener el resultado CAP-17 y exponer referencias transitorias
del mismo turno al runtime cognitivo. La incorporación del contenido recuperado a una
continuación investigativa queda fuera de alcance.
