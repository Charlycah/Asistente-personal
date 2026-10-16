# ROBY XI.2 — GATE 5.B.2
## Existing Official Capability Registry + Explicit Capability Dependency Metadata → Canonical RuntimeCapabilityGraph Provisioning Contract — CONTRACT BOUNDARY RECONCILIATION

Status: CONTRACT BOUNDARY RECONCILIATION — PENDING LOCAL CERTIFICATION  
Baseline de entrada: GATE 5.B.1 certificado — 14,002 PASS + Ruff limpio + 0 FAIL.

## 1. Propósito
Resolver, sin modificar producción, la pregunta que dejó abierta GATE 5.B.1: si el `OfficialRuntimeCapabilityRegistry` existente contiene metadata explícita, gobernada y suficiente para construir exactamente una instancia canónica de `RuntimeCapabilityGraph` sin inferir dependencias desde imports, wiring, nombres, tests, estructura de módulos o ejecución.

Este Gate no autoriza todavía CONTRACT RED ni SURGICAL GREEN. Su función es congelar el límite contractual entre:

`OfficialRuntimeCapabilityRegistry → explicit dependency declaration → RuntimeCapabilityGraph → OfficialROBYRuntime → UnifiedRuntimeObservability`.

## 2. Autoridades existentes preservadas
Se preservan sin duplicación:

- `core.capability_registry.CapabilityDescriptor`: descriptor canónico de una capacidad declarada.
- `app.runtime_capability_registry.OfficialRuntimeCapabilityRegistry`: source of truth ordenado de capacidades operacionales oficiales.
- `app.runtime_capability_registry.RuntimeCapabilityRegistration`: binding descriptor/interceptor/evidence-reader de una capacidad oficial.
- `app.runtime_capability_graph.RuntimeCapabilityGraph`: modelo canónico declarativo de dependencias entre capacidades.
- `app.runtime_capability_graph.RuntimeCapabilityNode`: nodo canónico del graph.
- `app.runtime_health_readiness.RuntimeCapabilityRequirement`: requisito operacional por capability y residents.
- `app.official_runtime_composition.OfficialROBYRuntime`: única autoridad de lifecycle/composición operacional oficial.
- `app.unified_runtime_observability.UnifiedRuntimeObservability`: proyección read-only unificada certificada.

No se introduce ni se recomienda `DependencyRegistry`, `CapabilityDependencyManager`, segundo graph ni segundo registry.

## 3. Inventario real de CapabilityDescriptor
`CapabilityDescriptor` contiene actualmente:

- identidad: `name`, `description`, `kind`;
- riesgo/permisos: `risk`, `permission_scope`, `requires_confirmation`;
- disponibilidad: `enabled`;
- semántica: `tags`, `semantic_triggers`, `supported_intents`, `example_utterances`;
- evidencia: `evidence_outputs`;
- iniciativa/efectos: `initiation_policy`, `effect_class`, `interaction_scope`;
- extensión genérica: `metadata: dict[str, str]`.

No existen campos canónicos `required_capabilities`, `optional_capabilities`, `depends_on`, `required_residents` u `optional_residents`.

Por tanto, el descriptor oficial **no expresa hoy el contrato del `RuntimeCapabilityNode`**.

## 4. Inventario real de OfficialRuntimeCapabilityRegistry.register(...)
El camino productivo principal `OfficialRuntimeCapabilityRegistry.register(...)` tampoco acepta dependency metadata explícita.

Al construir `CapabilityDescriptor`, fija `metadata` únicamente con:

- `runtime = official`;
- `interceptor = <tipo del interceptor>`.

Es decir, el caller no puede declarar mediante ese camino:

- required capability edges;
- optional capability edges;
- required residents;
- optional residents.

La ausencia es contractual, no sólo una falta de wiring posterior.

## 5. register_descriptor(...) y metadata genérica
`register_descriptor(...)` permite registrar un `CapabilityDescriptor` ya construido y, por tanto, preserva su `metadata` genérica.

Sin embargo, la búsqueda productiva actual encuentra un uso relevante para la biblioteca local cuya metadata declarada es únicamente:

`{"authority": "governed_local_library"}`.

No se encontró una convención productiva gobernada de keys de dependency graph dentro de `metadata`.

Consecuencia: **el diccionario genérico no puede reinterpretarse retrospectivamente como contrato de graph**. Hacerlo exigiría inventar key names, cardinalidad, semántica required/optional, validación y compatibilidad que hoy no existen.

## 6. RuntimeCapabilityRequirement tampoco está declarado productivamente
`RuntimeCapabilityRequirement` sí modela explícitamente:

- `capability_id`;
- `required_residents`;
- `optional_residents`;
- `requires_runtime`;
- `requires_supervisor`;
- `description`.

Pero no se encontraron construcciones productivas de `RuntimeCapabilityRequirement(...)` en `app/`, `core/` o `infrastructure/` que formen un catálogo oficial reusable para el graph.

Los usos existentes de requirements/graph son consumo por readiness/recovery o construcción en tests.

Por tanto, hoy falta también la mitad capability→resident del nodo canónico.

## 7. No equivalencias permitidas
Se encontraron otras nociones de dependencia en ROBY, pero no son equivalentes a capability graph metadata y no deben reutilizarse por similitud nominal:

- dependencias de tareas/planes;
- `UnifiedCognitiveCoordination.depends_on` para estrategia cognitiva;
- dependencias internas del `RuntimeCompositionRoot` entre objetos/wiring;
- requirements de device capabilities;
- imports de módulos;
- orden de construcción en `runtime_root_factory.py`.

Esas relaciones pertenecen a autoridades y semánticas distintas. Convertirlas automáticamente en edges de `RuntimeCapabilityGraph` violaría una autoridad por capacidad y produciría inferencia arquitectónica no declarada.

## 8. Matriz de metadata suficiente para provisioning

| Dato necesario para `RuntimeCapabilityNode` | Fuente oficial actual | ¿Explícito/gobernado? | Resultado |
|---|---|---:|---|
| capability id | `CapabilityDescriptor.name` | YES | AVAILABLE |
| description | `CapabilityDescriptor.description` | YES | AVAILABLE |
| required capability edges | ninguna | NO | NOT DECLARED |
| optional capability edges | ninguna | NO | NOT DECLARED |
| required residents | ninguna fuente oficial por capability | NO | NOT DECLARED |
| optional residents | ninguna fuente oficial por capability | NO | NOT DECLARED |
| runtime/supervisor requirement | defaults existen en `RuntimeCapabilityRequirement`, no declaration por capability | PARTIAL/IMPLICIT | INSUFFICIENT |
| enabled state | `CapabilityDescriptor.enabled` | YES | AVAILABLE, pero no es dependency metadata |
| interceptor identity | registry metadata | YES | AVAILABLE, pero no equivale a resident requirement |

Dictamen: **la metadata oficial actual no es suficiente para construir un graph canónico completo sin inferencia**.

## 9. Regla crítica: ausencia no significa dependencia vacía
No debe interpretarse la ausencia de dependency metadata como:

- `required_capabilities=()`;
- `optional_capabilities=()`;
- `required_residents=()`;
- `optional_residents=()`.

Eso convertiría “no declarado” en “declarado independiente”, fabricando conocimiento técnico.

La semántica correcta mientras no exista declaración explícita es:

**dependency graph: NOT PROVISIONED / dependency metadata: NOT DECLARED.**

## 10. Contrato mínimo de provisioning futuro
Si un futuro Gate autoriza implementación, el provisioning canónico deberá respetar simultáneamente:

1. **Declaración explícita:** cada nodo incluido se crea únicamente desde metadata tipada y gobernada, no desde scans/inferencia.
2. **Una sola identidad:** el `capability_id` del nodo debe corresponder exactamente a una capacidad oficial registrada.
3. **Required vs optional explícitos:** no inferir obligatoriedad por orden de wiring, uso o imports.
4. **Resident requirements explícitos:** no deducirlos del tipo de interceptor ni de nombres de componentes.
5. **Undeclared ≠ empty:** una capacidad sin declaración graph permanece fuera del graph o marcada como no declarada; nunca se presume independiente.
6. **Construcción única:** exactamente una instancia `RuntimeCapabilityGraph` por composición oficial, sólo después de tener declarations válidas.
7. **Ownership existente:** la instancia pertenece al runtime oficial/composición existente; no a un nuevo manager.
8. **Fail closed:** referencia a capability inexistente, ciclo, self-dependency o declaración inconsistente impide provisioning; no se corrige silenciosamente.
9. **Read-only publication:** observability publica sólo el snapshot/dependency view ya construido; no recalcula ni ejecuta readiness/recovery para observar edges.
10. **Analysis Mode consumidor:** TECHNICAL consume la proyección publicada y declara `not provisioned` cuando no existe graph válido.

## 11. ¿Debe CapabilityDescriptor.metadata convertirse en el contrato?
No en su forma actual.

`metadata: dict[str, str]` es extensible, pero carece de:

- tipos estructurados para listas required/optional;
- validación cruzada de capability ids;
- distinción robusta entre “no declarado” y “declarado vacío”;
- resident requirement schema;
- garantías de compatibilidad con `RuntimeCapabilityNode`.

Usar strings delimitados o keys ad hoc sería una nueva convención implícita y frágil. El futuro contrato debe ser **tipado y explícito dentro del camino de registro existente**, no un mini-registry oculto dentro de `metadata`.

## 12. Ownership y momento de construcción
GATE 5.B.1 ya estableció que el graph no debe tener una autoridad paralela. GATE 5.B.2 refina el límite:

- el registry sigue siendo source of truth de capabilities y sus declarations;
- el graph sigue siendo el modelo canónico derivado de declarations explícitas;
- el runtime oficial retiene la única instancia construida;
- `UnifiedRuntimeObservability` sólo lee esa instancia;
- Analysis Mode sólo lee observability.

La construcción debe ocurrir **después de finalizar el registro oficial y antes de publicar el runtime como composición plenamente provisionada**. El lugar exacto de wiring debe decidirse por el futuro RED/GREEN sin crear factory/manager paralelo si el runtime factory existente puede asumir esa costura.

## 13. Clasificación final de G5-R3b
G5-R3b queda ahora clasificado como:

**EXISTING OFFICIAL CAPABILITY REGISTRY + EXISTING CANONICAL RUNTIME CAPABILITY GRAPH + EXPLICIT GRAPH INPUT METADATA ABSENT — CANONICAL GRAPH PROVISIONING MUST REMAIN NOT_PROVISIONED UNTIL A TYPED DECLARATION CONTRACT EXISTS**

El problema no es falta de graph ni falta de registry. El residual es una **costura declarativa tipada** entre ambos.

## 14. Decisión sobre CONTRACT RED
Después de esta reconciliación sí existe un residual suficientemente pequeño y demostrable para un RED legítimo, pero el RED debe probar sólo el contrato declarativo/provisioning; no debe agregar observability completa, Analysis Mode, recovery ni readiness en el mismo incremento.

Próximo Gate recomendado:

**GATE 5.B.2.1 — Official Capability Registration Explicit Dependency Declaration → Canonical RuntimeCapabilityGraph Provisioning — CONTRACT RED**

El futuro RED debería congelar, como mínimo:

- declaration tipada dentro del camino de registro oficial existente;
- distinción undeclared vs explicit-empty;
- correspondencia descriptor/node;
- construcción de una sola instancia canónica;
- fail-closed ante edges inválidos/ciclos;
- ausencia honesta si no hay declarations suficientes;
- ninguna inferencia desde imports/wiring/nombres.

La exposición read-only del graph a `UnifiedRuntimeObservability` debe quedar para un Gate posterior si el provisioning primero se certifica correctamente.

## 15. Estado de residuales
- G5-R3a operational/errors/health/readiness/capabilities: CLOSED.
- G5-R3b capability dependencies: OPEN NARROW — explicit declaration/provisioning seam isolated.
- G5-R3c episodes/budgets: OPEN DEFERRED.
- G5-R3d versions: OPEN DEFERRED.
- G5-R3e certifications/quality: OUTSIDE CURRENT RUNTIME OBSERVABILITY.
- G5-R4 architectural evidence: DELIBERATELY OPEN / OUTSIDE THIS GATE.

## 16. Cambios productivos
Ninguno.

Este Gate modifica únicamente documentación de reconciliación/estado y la baseline de calidad generada por el procedimiento normal de certificación.

## 17. STOP
No implementar dependency fields todavía. No crear graph builder/manager/registry paralelo. No reinterpretar `metadata` genérica. No inferir edges/residents desde imports, wiring, tests, nombres o tipos. No publicar graph en observability todavía. No ejecutar readiness/recovery para llenar Analysis Mode. No abrir episodes/budgets, versions, certifications ni G5-R4. No activar diagnostics, Reasoning, Planning, Reflection, Memory o Learning automáticamente.
