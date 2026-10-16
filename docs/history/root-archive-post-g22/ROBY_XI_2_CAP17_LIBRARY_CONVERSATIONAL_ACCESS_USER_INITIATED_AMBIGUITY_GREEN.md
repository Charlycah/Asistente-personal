# ROBY XI.2 — CAP-17 GREEN
## Library Conversational Access — User Initiated + Ambiguity

Estado: GREEN quirúrgico de acceso conversacional solicitado por usuario.

## Alcance implementado

- `OfficialKnowledgeRuntimeGateway` reconoce semántica de Biblioteca (`biblioteca`,
  `mis libros`) como `KnowledgeSourceKind.LOCAL_DOCUMENTS`.
- Una petición local explícita deja de caer en WEB sólo por contener el verbo
  genérico `buscá`.
- `GovernedLibraryConversationalSelectionV1` resuelve estrictamente 0/1/N:
  - 0 -> `NO_MATCH`;
  - 1 -> selección explícita y trazable;
  - N -> `NEEDS_DISAMBIGUATION`, sin lectura implícita.
- `GovernedLocalLibraryConversationV1` compone las autoridades ya existentes:
  catálogo -> selección -> handoff certificado -> binding one-shot -> Unified
  Retrieval Runtime -> artefacto canónico `LOCAL_DOCUMENTS`.
- La provenance (`source_reference`) sobrevive hasta el resultado conversacional.

## Límites preservados

- Sólo user-initiated en este incremento.
- No iniciativa autónoma de ROBY.
- No `matches[0]` cuando hay ambigüedad.
- No Memory ni Learning.
- No modificación de `KnowledgeRetrievalStep`.
- No nuevo retrieval orchestrator, execution gateway o runtime root.
- No persistencia de selección.
- No cambio de `.roby/config.json`.
- No EPUB en este incremento.

## STOP

El siguiente gate debe reconciliar por separado la iniciativa de ROBY para consultar
la Biblioteca bajo la autoridad de independencia/governance existente.
