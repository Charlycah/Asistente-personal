# ROBY XI.2 — INTEL-G9 — Source-neutral certified governed memory write request → existing productive wiring → OfficialMemoryGateway productive reachability — CONTRACT RED

## Estado

CONTRACT RED. Baseline de entrada: INTEL-G8 source-neutral materialization → existing governed memory write adapter SURGICAL GREEN certificado, **14.113 PASS · Ruff clean · 0 FAIL · 0 regressions**.

## Propósito

Congelar el residual productivo posterior a G8 sin reabrir autorización, materialización ni adaptación: un `GovernedMemoryWriteRequest` source-neutral ya certificado debe poder alcanzar el `OfficialMemoryGateway` exclusivamente a través del `ProductiveGovernedLearningWiring` existente.

## Autoridades preservadas

- `ProductiveGovernedLearningWiring` continúa siendo la única autoridad productiva de este flujo.
- `GovernedMemoryWriteAdapterFoundation` continúa siendo el único adapter gobernado y este gate consume su request ya certificado.
- `OfficialMemoryGateway` continúa siendo la única autoridad de escritura de Memory.
- La ruta histórica Curiosity/Preference permanece intacta.

No se crea writer, gateway, adapter, manager, planner, authorization boundary ni productive wiring paralelo.

## Seam contractual mínimo

El seam faltante se congela en la frontera ya reconciliada:

`GovernedMemoryWriteRequest` → existing `ProductiveGovernedLearningWiring` → existing `OfficialMemoryGateway.remember_governed_learning(...)`.

La entrada propuesta para CONTRACT RED es `execute_certified_write_request(request)`. Este método no evalúa, autoriza, materializa ni adapta: consume exclusivamente un `GovernedMemoryWriteRequest` que ya porta la autoridad/componente/método de escritura certificados.

## Semántica que debe reutilizar

El seam source-neutral debe reutilizar la semántica productiva ya existente en el wiring histórico:

- gateway ausente → `MEMORY_UNAVAILABLE`, sin cola ni persistencia alternativa;
- excepción del writer → `WRITE_FAILED`, contenida y sin propagación;
- `stored_count > 0` → `STORED`;
- `stored_count == 0` → `ALREADY_STORED`;
- preservar exactamente el `GovernedMemoryWriteRequest` recibido;
- `writer_call_performed` verdadero sólo para los outcomes persistentes existentes;
- conservar idempotencia del `OfficialMemoryGateway`.

## Lineage source-neutral

Una escritura G8 productiva válida debe persistir como `LearningCategory.STABLE_KNOWLEDGE`, conservar `policy_candidate_id` y no fabricar `preference_candidate_id`, `PreferenceCandidate`, `learning_kind` ni `CuriosityLearningKind.PREFERENCE`.

## Invariantes

`APPROVED != MATERIALIZED`

`MATERIALIZATION PROPOSAL != WRITE REQUEST`

`WRITE REQUEST != PERSISTED MEMORY`

La transición a memoria persistida ocurre solamente cuando el request certificado atraviesa el existing `ProductiveGovernedLearningWiring` y alcanza el existing `OfficialMemoryGateway`.

## Prohibiciones

Este gate no puede:

- conectar G7 o G8 directamente al gateway;
- volver a ejecutar G6/G7/G8;
- volver a materializar una propuesta;
- volver a adaptar el request dentro del nuevo seam;
- fabricar provenance Preference/Curiosity;
- crear una autoridad de autorización de escritura;
- introducir un segundo wiring, writer o MemoryGateway;
- cambiar persistencia/runtime salvo que un RED posterior demuestre un residual real adicional.

## RED esperado

Los tests contractuales deben fallar únicamente porque `ProductiveGovernedLearningWiring` todavía no expone el seam source-neutral `execute_certified_write_request(...)`.

El código productivo permanece intacto durante CONTRACT RED.
