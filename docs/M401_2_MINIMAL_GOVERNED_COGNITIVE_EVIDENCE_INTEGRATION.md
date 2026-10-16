# ROBY XI.2 — M401.2 Minimal Governed Cognitive Evidence Integration

**Base:** M400.9 + Canonical Documentation Sync Post-M400.9  
**Estado:** candidato para validación  
**Alcance:** integración cognitiva mínima de evidencia M400; sin adquisición externa nueva.

## Objetivo

Demostrar la ruta mínima mediante la cual evidencia M400 ya existente puede participar de
forma transitoria, explícita, trazable y no autoritativa en el `CognitiveRuntimeOrchestrator`
existente, sin crear un cerebro, autoridad, manager, orchestrator o composition root paralelo.

## Gate A — resultado

El contrato existente no podía transportar evidencia M400 estructurada sin pérdida:
`LLMRequest.metadata` es `dict[str, str]` y `CognitiveRuntimeOrchestrator.enrich()` no recibía
un objeto estructurado de evidencia externa. Por ello se autorizó un único cambio contractual
backward-compatible dentro del runtime cognitivo existente.

## Cambio mínimo

Se incorpora `core/cognitive_runtime_orchestration/external_evidence.py` con:

- `CognitiveExternalEvidenceAdmissionStatus`;
- `CognitiveExternalEvidenceLineage`;
- `CognitiveExternalEvidenceAdmission`;
- adaptación determinista a `CognitiveRuntimeContribution`.

`CognitiveRuntimeOrchestrator.enrich()` recibe opcionalmente `external_evidence=()` y, sólo
cuando existe evidencia admitida, la agrega como stage reservado `external_evidence` dentro
del mismo `[Contexto cognitivo gobernado]` que ya utiliza ROBY.

## Invariantes preservados

- evidencia externa ≠ conocimiento interno;
- confianza ≠ certeza;
- corroboración ≠ verdad;
- información externa ≠ autoridad cognitiva;
- rejected stays rejected;
- lineage M400 se conserva mediante referencias tipadas a envelope/verification/assessment;
- no persistencia automática;
- no execution authority;
- M400 no depende de cognición;
- ausencia de evidencia externa conserva exactamente el comportamiento previo.

## Fuera de alcance

M401.2 **no** modifica:

- `RuntimeCompositionRoot`;
- `GovernedRuntimePreparation`;
- `CognitivePipeline`;
- `OfficialConversationGateway`;
- memoria, learning, planning o knowledge;
- ejecución de providers o fuentes;
- adquisición productiva pre-inferencia.

La adquisición productiva de evidencia antes de inferencia continúa siendo un gate separado
y no queda autorizada por este incremento.

## Evidencia de pruebas previa al handoff

- tests M401.2 + M189: 21 passed;
- suite dirigida M177/M178/M189/M400/M401.2: 106 passed;
- compilación Python: limpia;
- Ruff no disponible en el entorno de construcción; requiere validación oficial del usuario.

## Impacto en Plan Maestro

**IMPACTO EN PLAN MAESTRO:** completa únicamente la frontera de consumo cognitivo mínimo de
M400; no desplaza Residential Node, Governed Synchronization ni Residential Perception.

**DECISIÓN PREVIA QUE PRESERVA:** M395 mantiene único runtime cognitivo, único composition
root y única frontera conversacional.

**PENDIENTE QUE RESUELVE:** M400 podía producir evidencia gobernada pero no existía un canal
estructurado directo para que el runtime cognitivo existente la consumiera.

**NUEVO HUECO CREADO:** adquisición productiva pre-inferencia queda explícitamente diferida;
no se abre automáticamente otro milestone.
