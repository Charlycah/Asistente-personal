# ROBY XI.2 — CAP-17 — Productive Runtime Wiring — Contract RED

## Base certificada

Este RED se apoya en `ROBY_XI_2_CAP17_GOVERNED_ROBY_INITIATED_LIBRARY_ACCESS_GREEN_CORREGIDO.zip`, cuya certificación oficial es **13.806 PASS + Ruff limpio**.

## Objetivo

Congelar el contrato mínimo para conectar CAP-17 al único runtime productivo oficial, sin crear una nueva autoridad, sin ampliar formatos documentales y sin modificar `.roby/config.json`.

## Frontera

Este bloque es exclusivamente de composición productiva. EPUB queda expresamente fuera y conserva su RED/GREEN propio. `Documentos` no se incorpora como segundo root ni como alias de Biblioteca.

## Contrato congelado

1. `OfficialRuntimeCapabilityRegistry` debe poder registrar un `CapabilityDescriptor` canónico sin redeclarar sus campos.
2. `RuntimeCompositionDependencies` debe exponer exactamente un wiring CAP-17 productivo.
3. El root productivo debe reconocer configuración explícita `ROBY_LOCAL_LIBRARY_ROOT`.
4. `runtime_root_factory.py` debe construir CAP-17 mediante un builder gobernado, no inline duplicando lógica.
5. Debe existir `app.governed_local_library_runtime_wiring` como módulo instrumental de composición.
6. El estado de provisión debe distinguir `not_provisioned`, `invalid_configuration` y `provisioned`.
7. El builder recibe las autoridades existentes: `knowledge_runtime`, `unified_runtime`, `capability_registry`.
8. Un único catálogo debe ser compartido por la conversación productiva.
9. La authorization boundary debe quedar expuesta y construida sobre el manager del registry oficial.
10. El adapter ROBY-initiated debe quedar construido sobre esa misma boundary.
11. Debe existir un interceptor user-initiated para el puerto conversacional oficial.
12. El wiring debe exponer estado auditable: root configurado y límite de catálogo.
13. El capability name sigue siendo `knowledge.local_library.read`.
14. El descriptor productivo debe ser el descriptor canónico de `core.governed_local_library.initiative`.
15. El interceptor no puede convertirse en router/planner/authorization authority alternativo.
16. No hay scan/watch/polling/background.
17. EPUB no se implementa ni se finge en este bloque.
18. `KnowledgeRetrievalStep` conserva exactamente su esquema actual.
19. El wiring no administra ni escribe `.roby/config.json`.
20. El contrato preserva los bytes de `.roby/config.json`.

## Semántica GREEN esperada

- Sin `ROBY_LOCAL_LIBRARY_ROOT`: runtime arranca y CAP-17 queda `not_provisioned`.
- Root inválido: `invalid_configuration`, sin fallback a HOME/cwd/D: y sin registro productivo de la capacidad.
- Root válido: una sola biblioteca, un solo reader, una sola conversation path y una sola authorization boundary.
- El descriptor canónico se registra una sola vez en `OfficialRuntimeCapabilityRegistry`.
- `GovernedIndependenceAuthorizationBoundaryV1` usa `capability_registry.manager`.
- El user-initiated path entra por el interceptor oficial y conserva 0/1/N.
- El adapter ROBY-initiated queda disponible pero este bloque no inventa el productor cognitivo de propuestas.
- `NO_MATCH` no hace fallback automático a WEB.
- El Unified Retrieval Runtime existente sigue siendo el único ejecutor de adquisición CAP-17.

## RED intencional

Producción no se modifica. Los veinte tests de este contrato deben fallar únicamente porque el wiring productivo todavía no existe o porque el registry/root todavía no expone los puntos de composición requeridos.
