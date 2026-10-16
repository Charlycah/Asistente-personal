# ROBY XI.2 — CAP-17 — RED contractual
## Cognitive Evidence Need → Local Library Proposal

Base oficial de partida: **CAP-17 EPUB Library Reading Support GREEN — 13.840 PASS + Ruff limpio**.

Este RED abre únicamente el eslabón productivo faltante entre una necesidad cognitiva de evidencia ya producida por `governed_reasoning` y la iniciativa gobernada de Biblioteca ya certificada.

### Contrato

- La necesidad entra de forma estructurada mediante `DiscriminatingEvidenceRequirement`; no se fabrica texto conversacional.
- `OfficialKnowledgeRuntimeGateway` obtiene un `KnowledgeSourceNeed` estructurado preservando la semántica de `missing_evidence_descriptions`.
- `KnowledgeSourcePolicy` conserva la autoridad de decidir fuente.
- Sólo `LOCAL_SOURCE_PREFERRED` puede producir/entregar una propuesta a `GovernedRobyInitiatedLibraryAccessV1`.
- La propuesta conserva `source_reference`, `world_snapshot_id`, `requirement_id` y `source_decision_id`.
- Biblioteca no disponible falla cerrada y no inicia búsqueda/lectura.
- El bridge no busca ni lee libros directamente.
- La autorización existente sigue siendo el gate previo a cualquier búsqueda.
- Usuario y ROBY convergen mediante una ruta neutral `handle_admitted_request`; ROBY deja de simular una petición humana.
- Se mantiene intacto el contrato de selección explícita 0/1/N.
- No se modifica `KnowledgeRetrievalStep`.
- No Memory, Learning, background scan, root hardcodeado ni nueva autoridad cognitiva.

### Producción

Este ZIP RED **no modifica código de producción**. Sólo añade el contrato RED y este documento.
