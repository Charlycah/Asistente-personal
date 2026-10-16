# M400.4 — Governed External Information Source Integration

## Propósito

M400.4 conecta la familia `Information Source` de M400.2 con la infraestructura
de fuentes externas ya gobernada. No crea un source manager, no ejecuta red y
no habilita adapters.

La integración recibe un `GovernedSourceQueryResult` ya producido por
`OfficialConversationGateway` / `GovernedSourceQueryExecutor` y lo transforma
en un `ExternalIntelligenceEnvelope`:

**source execution → external evidence envelope**

## NASA y demás fuentes

NASA es una fuente, no un LLM provider. M400.4 mantiene separadas las familias
`Information Source` e `Inference Provider`.

El adapter NASA continúa bajo la autoridad existente de
`OfficialConversationGateway`, con consulta explícita y sin fetch automático.
M400.4 no llama `execute()`, no registra adapters y no habilita fuentes.

## Estados de consulta

Una consulta `succeeded` entra como evidencia aceptada con sus items.

Una consulta `empty` entra como evidencia aceptada vacía. La ausencia de
resultados no se convierte en información inventada.

Una consulta `failed` entra como evidencia rechazada con el tipo de error
gobernado. El fallo de una fuente no se interpreta como afirmación de la fuente.

## Procedencia

La procedencia conserva:

- `source_id`;
- `source_status`;
- `source_error` cuando existe;
- timestamp de recepción;
- scope de ejecución;
- uso de red explícito.

`execution_scope` y `network_used` permanecen separados. La integración no
deduce transporte a partir del tipo de fuente.

## Autoridad

**capacidad/evidencia externa ≠ autoridad cognitiva**

`GovernedExternalInformationSourceIntegration` expone `integration_id`, no
`authority_id`. ROBY conserva interpretación, contraste y decisión.

M400.4:

- no ejecuta ni habilita fuentes;
- no reemplaza `OfficialConversationGateway`;
- no reemplaza `GovernedSourceQueryExecutor`;
- no reemplaza `KnowledgeSourcePolicy`;
- no fusiona NASA con providers LLM;
- no agrega polling, background ni fetch automático;
- no modifica memoria, planificación ni código operativo.
