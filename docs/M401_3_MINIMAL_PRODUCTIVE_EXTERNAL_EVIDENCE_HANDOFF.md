# M401.3 — Minimal Productive External Evidence Handoff

## Alcance

M401.3 transporta una admisión M401.2 ya construida, explícita y perteneciente al turno actual desde la frontera conversacional productiva hasta el `CognitiveRuntimeOrchestrator` antes de la inferencia.

No adquiere evidencia. No selecciona fuentes. No ejecuta providers. No reconsulta. No persiste evidencia.

## Ruta

`OfficialConversationGateway.submit(external_evidence=...)` → `EndToEndLocalConversation.converse(...)` → `GovernedConversationPipelineRequest.external_evidence` → `GovernedRuntimePreparation` → `CognitiveRuntimeOrchestrator.enrich(external_evidence=...)` → inferencia existente.

La ausencia de evidencia conserva el flujo histórico y no provoca ejecución externa adicional.

## Invariantes

- evidencia externa ≠ conocimiento interno
- confianza ≠ certeza
- corroboración ≠ verdad
- información externa ≠ autoridad cognitiva
- M401 consume evidencia ya obtenida; no adquiere ni reconstruye evidencia
- flujo explícito por turno; sin globals, last-result ni cache implícita
- `truth_certified=False`
- `cognitive_authority_granted=False`
- `persistence_authorized=False`
- `execution_authorized=False`
- un único ROBY / un único cerebro / una única autoridad por capacidad

## Límite de cierre

Este incremento cierra únicamente el handoff productivo. Las autoridades de adquisición/routing/execution existentes permanecen fuera de M401. Cualquier adquisición automática, polling, background fetching o nuevo subsistema requiere un gate separado y no queda autorizado por M401.3.
