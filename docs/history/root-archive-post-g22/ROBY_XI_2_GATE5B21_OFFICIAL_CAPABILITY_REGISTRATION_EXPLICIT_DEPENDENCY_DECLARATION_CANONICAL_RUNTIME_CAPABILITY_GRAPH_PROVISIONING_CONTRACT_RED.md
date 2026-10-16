# ROBY XI.2 — GATE 5.B.2.1
## Official Capability Registration Explicit Dependency Declaration → Canonical RuntimeCapabilityGraph Provisioning — CONTRACT RED

### Baseline de entrada certificada
- GATE 5.B.2 Contract Boundary Reconciliation: certificado y cerrado.
- M361 sincronizado.
- Ruff limpio.
- pytest: 14,002 PASS.
- 0 FAIL.

## Propósito
Congelar contractualmente el único residual estrecho autorizado por GATE 5.B.2 antes de modificar producción: permitir que el registro oficial declare dependencias de capability de forma **tipada, explícita y gobernada**, y que el runtime oficial pueda provisionar exactamente una instancia canónica de `RuntimeCapabilityGraph` únicamente a partir de esas declaraciones.

Este RED no añade una nueva autoridad y no expone todavía el graph en `UnifiedRuntimeObservability` ni en Analysis Mode.

## Autoridades preservadas
- `CapabilityDescriptor`: descriptor canónico existente; `metadata` genérica no se convierte en dependency schema.
- `OfficialRuntimeCapabilityRegistry`: única source of truth ordenada de capabilities operacionales y futura fuente de declaraciones explícitas.
- `RuntimeCapabilityRegistration`: binding existente descriptor/interceptor/evidence-reader; puede transportar un value object subordinado de declaración.
- `RuntimeCapabilityRequirement`: contrato existente capability→resident.
- `RuntimeCapabilityNode` / `RuntimeCapabilityGraph`: modelo canónico existente de dependencias.
- `OfficialROBYRuntime`: única autoridad existente que debe poseer la instancia productiva del graph.

No se crea `DependencyRegistry`, `CapabilityDependencyManager`, segundo graph, segundo registry ni runtime paralelo.

## Contrato RED
El contrato exige simultáneamente:

1. Existe un value object inmutable y tipado `RuntimeCapabilityDependencyDeclaration` dentro del módulo de registro existente.
2. La declaración expresa exactamente: `required_capabilities`, `optional_capabilities`, `required_residents`, `optional_residents`, `requires_runtime` y `requires_supervisor`.
3. `RuntimeCapabilityRegistration` conserva opcionalmente esa declaración sin codificarla en `CapabilityDescriptor.metadata`.
4. Tanto `OfficialRuntimeCapabilityRegistry.register(...)` como `register_descriptor(...)` aceptan el mismo contrato tipado opcional.
5. `dependency_declaration=None` significa **NOT DECLARED**; no equivale a una declaración vacía.
6. Una instancia explícita con todas las colecciones vacías significa **DECLARED EMPTY / explicit independent**.
7. El registry expone una proyección read-only `declared_capability_nodes()`; no construye ni posee un graph.
8. Sólo las registrations con declaración explícita se materializan como `RuntimeCapabilityNode`.
9. La conversión declaration→node reutiliza `RuntimeCapabilityRequirement` y preserva exactamente residents, flags runtime/supervisor, description y capability id.
10. Required/optional capability edges pasan literalmente al `RuntimeCapabilityNode`; no se infieren por imports, wiring, orden, interceptor o nombres.
11. `RuntimeCapabilityGraph` continúa siendo quien valida referencias inexistentes, self-dependencies, duplicados y ciclos, fail-closed.
12. `OfficialROBYRuntime` puede poseer como máximo una instancia `capability_graph`, opcional cuando no hay declarations provisionables.
13. El factory/composition oficial construye esa instancia únicamente después de completar el registro y únicamente desde `declared_capability_nodes()`.
14. Si no existe ninguna declaración explícita, el runtime conserva `capability_graph=None`; no fabrica un graph vacío como conocimiento técnico.
15. `with_residents(...)` y `with_resident_registry(...)`, si reconstruyen `OfficialROBYRuntime`, deben preservar la misma instancia canónica de graph; no recalcularla.
16. Este Gate no modifica `UnifiedRuntimeObservability`, Analysis Mode, readiness/recovery semantics ni ejecuta graph evaluation.
17. `.roby/config.json` permanece byte-identical; `credencial.json`, si existe, se preserva.

## API contractual congelada para GREEN
El RED congela la mínima costura nominal necesaria para evitar una implementación estética alternativa que vuelva ambiguo el ownership:

- value object: `RuntimeCapabilityDependencyDeclaration`;
- campo subordinado: `RuntimeCapabilityRegistration.dependency_declaration`;
- parámetros opcionales homónimos `dependency_declaration` en `register(...)` y `register_descriptor(...)`;
- proyección read-only: `OfficialRuntimeCapabilityRegistry.declared_capability_nodes()`;
- ownership: `OfficialROBYRuntime.capability_graph` y parámetro constructor homónimo.

`declared_capability_nodes()` es una proyección, no una autoridad ni un builder de graph. El único constructor del graph sigue siendo `RuntimeCapabilityGraph(...)` en la composición/runtime oficial.

## RED esperado
Sobre la baseline certificada 14,002 PASS deben fallar exclusivamente las costuras todavía ausentes:

1. value object tipado de dependency declaration;
2. campo de declaration en `RuntimeCapabilityRegistration`;
3. parámetro en `register(...)`;
4. parámetro en `register_descriptor(...)`;
5. proyección `declared_capability_nodes()`;
6. distinción ejecutable undeclared vs explicit-empty;
7. materialización exacta declaration→existing node/requirement;
8. ownership `OfficialROBYRuntime.capability_graph`;
9. provisioning desde el factory oficial.

Las validaciones ya existentes de `RuntimeCapabilityGraph`, las prohibiciones de autoridad paralela, `.roby/config.json` y el STOP de observability deben permanecer verdes.

## STOP
Este Gate termina en **CONTRACT RED**.

No modificar producción. No implementar GREEN. No declarar dependencias reales de las capabilities existentes todavía. No exponer graph en `UnifiedRuntimeObservability` ni Analysis Mode. No abrir episodes/budgets, versions, certifications ni G5-R4. No inferir dependencias desde imports, wiring, nombres, interceptors, tests o scans.

La transición a SURGICAL GREEN sólo se autoriza después de certificación local del usuario demostrando que Ruff permanece limpio y que la suite completa falla únicamente por estas costuras RED esperadas.
