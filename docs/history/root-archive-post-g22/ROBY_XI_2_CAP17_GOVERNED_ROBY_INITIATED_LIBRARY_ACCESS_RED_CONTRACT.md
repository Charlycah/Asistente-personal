# ROBY XI.2 — CAP-17 RED contractual
## Governed ROBY-Initiated Library Access

**Base oficial de entrada:** CAP-17 Library Conversational Access — User Initiated + Ambiguity GREEN, 13.784 PASS + Ruff limpio.

## Propósito

Congelar antes del GREEN el contrato por el cual ROBY puede proponer e iniciar una consulta read-only a la Biblioteca local sin fingir una solicitud humana, sin crear una segunda autoridad y sin desviar CAP-17 hacia el pipeline histórico de Evidence Acquisition.

## Autoridad

La autorización debe seguir perteneciendo a `GovernedIndependenceAuthorizationBoundaryV1`. El RED exige una entrada genérica `evaluate_capability_initiation(...)` para una solicitud read-only explícita, conservando `MAY_INITIATE`, `MUST_ASK`, `MUST_ABSTAIN` y `REVIEW_REQUIRED`.

La capacidad debe ser `knowledge.local_library.read` y usar `CapabilityRegistryManager`, con perfil inicial `LOW + READ + GOVERNED_AUTONOMOUS + READ_ONLY + INTERNAL + requires_confirmation=False`.

## Composición exigida

`propuesta consultiva -> CapabilityRegistry -> GovernedIndependenceAuthorizationBoundaryV1 -> gate -> realización transparente -> CAP-17 0/1/N -> handoff -> binding one-shot -> Unified Retrieval Runtime -> Knowledge artifact -> STOP`

`MAY_INITIATE` sólo autoriza iniciar la capacidad. No autoriza seleccionar silenciosamente un libro.

## Invariantes contractuales

1. `knowledge.local_library.read` usa el Capability Registry oficial.
2. Perfil LOW + READ + GOVERNED_AUTONOMOUS + READ_ONLY + INTERNAL.
3. La propuesta interna no ejecuta antes de autorización.
4. La misma `GovernedIndependenceAuthorizationBoundaryV1` autoriza.
5. MAY_INITIATE habilita el adapter CAP-17.
6. MUST_ASK: cero búsquedas/lecturas.
7. MUST_ABSTAIN: cero búsquedas/lecturas.
8. REVIEW_REQUIRED: cero búsquedas/lecturas.
9. No se fabrica `DiscriminatingEvidenceRequirement`.
10. No se usa `GovernedLevel2ReadOnlyExecutionGatewayV1` como segundo ejecutor.
11. MAY_INITIATE conserva 0/1/N.
12. N candidatos -> NEEDS_DISAMBIGUATION y cero lecturas.
13. Un candidato conserva selección/provenance/fingerprint mediante CAP-17.
14. Adquisición por el mismo binding one-shot + Unified Retrieval Runtime.
15. “voy a consultar la Biblioteca…” sólo deriva de MAY_INITIATE.
16. Sin scan/background/polling.
17. Sin Memory/Learning.
18. `KnowledgeRetrievalStep` permanece sin cambios.
19. `.roby/config.json` permanece sin cambios.
20. La rama User-Initiated debe seguir verde.
21. La autorización/selección no se reutiliza en otra ejecución.
22. NO_MATCH no hace fallback silencioso a WEB.

## Superficie contractual esperada por el GREEN

- `core.governed_local_library.initiative.governed_local_library_read_descriptor()`.
- `GovernedReadOnlyCapabilityInitiationRequest` en la autoridad de independencia existente.
- `GovernedIndependenceAuthorizationBoundaryV1.evaluate_capability_initiation(...)`.
- `app.governed_roby_initiated_library_access.GovernedRobyInitiatedLibraryAccessV1`.
- Reutilización de `GovernedLocalLibraryConversationV1` después del gate, mediante una operación neutral/admitida; no se debe falsificar texto humano para entrar por `handle_user_request`.

## STOP

Este RED no autoriza runtime-root wiring, iniciativa residente continua, watchers, indexación de fondo, Memory/Learning ni cambios en `.roby/config.json`.
