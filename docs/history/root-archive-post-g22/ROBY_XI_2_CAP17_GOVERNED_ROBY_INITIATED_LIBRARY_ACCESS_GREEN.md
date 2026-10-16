# ROBY XI.2 — CAP-17 GREEN — Governed ROBY-Initiated Library Access

## Alcance

GREEN quirúrgico del contrato CAP-17 para permitir que ROBY proponga una consulta
read-only a la Biblioteca local y la ejecute únicamente cuando la autoridad de
independencia existente devuelve `MAY_INITIATE`.

## Autoridad preservada

No se crea una segunda autoridad de autonomía. Se amplía
`GovernedIndependenceAuthorizationBoundaryV1` con una entrada genérica
`evaluate_capability_initiation(...)` para capacidades Level-2 read-only. La decisión
continúa siendo `MAY_INITIATE`, `MUST_ASK`, `MUST_ABSTAIN` o `REVIEW_REQUIRED`.

## Capacidad declarada

`knowledge.local_library.read` se describe mediante el `CapabilityDescriptor` oficial:
riesgo LOW, permiso READ, política GOVERNED_AUTONOMOUS, efecto READ_ONLY, ámbito
INTERNAL y sin confirmación obligatoria por defecto.

## Ejecución

`MAY_INITIATE` no ejecuta por sí mismo ni selecciona documentos. El adapter
`GovernedRobyInitiatedLibraryAccessV1` emite transparencia y reutiliza
`GovernedLocalLibraryConversationV1`, preservando catálogo, selección 0/1/N,
handoff explícito, binding one-shot y Unified Retrieval Runtime.

`MUST_ASK`, `MUST_ABSTAIN` y `REVIEW_REQUIRED` detienen el flujo antes de toda búsqueda
o lectura. `NO_MATCH` se detiene sin fallback automático a WEB.

## Límites

No Memory/Learning, no watcher/polling/background, no segundo ejecutor Level-2, no
cambio de `KnowledgeRetrievalStep`, no modificación de `.roby/config.json`.

## Validación dirigida del entorno de integración

- Contrato CAP-17 ROBY-initiated: 22 passed.
- CAP-17 + Independence Authorization + Level-2 Read-Only: 116 passed.
- `compileall`: limpio.
- Ruff no disponible en este entorno; certificación completa queda a cargo del usuario.
