# ROBY XI.2 — GATE 5.B.2.1
## Official Capability Registration Explicit Dependency Declaration → Canonical RuntimeCapabilityGraph Provisioning — SURGICAL GREEN

### Baseline de entrada certificada
- GATE 5.B.2: 14,002 PASS + Ruff limpio + 0 FAIL.
- CONTRACT RED GATE 5.B.2.1: 14,007 PASS + exactamente 9 FAIL contractuales esperados + Ruff limpio + 0 FAIL externos.
- El test RED corregido por el usuario queda integrado como contrato canónico.

## Propósito
Cerrar exclusivamente la costura declarativa/provisioning aislada por GATE 5.B.2: permitir declaraciones de dependencia explícitas y tipadas dentro del registro oficial existente, proyectarlas al `RuntimeCapabilityGraph` canónico existente y retener como máximo una instancia oficial del graph en `OfficialROBYRuntime`.

Este GREEN no declara dependencias reales para las capabilities productivas existentes y no publica el graph en `UnifiedRuntimeObservability` ni Analysis Mode.

## Cambios productivos quirúrgicos
### `app/runtime_capability_registry.py`
Se añade el value object subordinado e inmutable `RuntimeCapabilityDependencyDeclaration` con exactamente:
- `required_capabilities`
- `optional_capabilities`
- `required_residents`
- `optional_residents`
- `requires_runtime`
- `requires_supervisor`

`RuntimeCapabilityRegistration` conserva opcionalmente `dependency_declaration`.

`OfficialRuntimeCapabilityRegistry.register(...)` y `register_descriptor(...)` aceptan el mismo parámetro opcional tipado. `None` conserva el significado **NOT DECLARED**; una instancia explícita vacía significa **DECLARED EMPTY**.

Se añade `declared_capability_nodes()`, proyección read-only que:
- omite registrations sin declaración;
- reutiliza `RuntimeCapabilityRequirement` y `RuntimeCapabilityNode` existentes;
- preserva id, description, residents, flags runtime/supervisor y capability edges exactamente;
- no construye ni posee un graph;
- no infiere dependencias desde metadata, imports, wiring, nombres o interceptors.

### `app/official_runtime_composition.py`
`OfficialROBYRuntime` acepta y retiene opcionalmente `capability_graph` y lo expone mediante propiedad read-only homónima.

`with_residents(...)` y `with_resident_registry(...)` preservan la misma instancia recibida; no recalculan el graph.

`build_official_runtime_from_environment()` consulta únicamente `root.dependencies.official_capability_registry.declared_capability_nodes()`. Construye `RuntimeCapabilityGraph(...)` sólo si existen nodos declarados. Si no existe ninguna declaración explícita, conserva `capability_graph=None`; no fabrica un graph vacío.

`RuntimeCapabilityGraph` permanece única autoridad de validación fail-closed para referencias inexistentes, self-dependencies, duplicados y ciclos.

## Autoridades preservadas
- `OfficialRuntimeCapabilityRegistry`: source of truth de registrations y declarations explícitas.
- `RuntimeCapabilityRequirement`: contrato capability→resident existente.
- `RuntimeCapabilityNode` / `RuntimeCapabilityGraph`: modelo canónico existente.
- `OfficialROBYRuntime`: owner de la única instancia productiva del graph.

No se crea `DependencyRegistry`, `CapabilityDependencyManager`, `TechnicalInventoryManager`, segundo registry, segundo graph ni runtime paralelo.

## Semántica cerrada
1. `undeclared != explicit-empty` queda representado directamente en el modelo.
2. Sólo declarations explícitas producen nodos.
3. El registry no adquiere ownership del graph.
4. El runtime no inventa conocimiento técnico cuando no hay declarations.
5. La construcción se realiza desde declarations explícitas y falla cerrada mediante el graph canónico si la declaration es inválida.
6. Reconfigurar residents preserva la identidad del graph ya provisionado.

## Validación de implementación
En el entorno de integración:
- contrato GATE 5.B.2.1 corregido: 14 PASS;
- bundle focal registry/runtime/graph/readiness/recovery/observability/M395.5: 98 PASS;
- compilación de los módulos modificados: correcta.

Ruff no está instalado en este entorno, por lo que la certificación integral corresponde al usuario.

## Integridad
- `.roby/config.json` permanece byte-identical con SHA-256 `11a1dce801533fbe42bb37596e5273e2c9c99d52b2b26c625b7f54ee845132b5`.
- `credencial.json` no está presente en esta baseline; no fue eliminado ni modificado.
- `UnifiedRuntimeObservability` no se modifica en este Gate.

## Estado
**SURGICAL GREEN IMPLEMENTADO / PENDIENTE DE CERTIFICACIÓN LOCAL INTEGRAL.**

La baseline oficial no cambia hasta que el usuario certifique `ruff check .` y la suite completa con 0 FAIL.

## STOP
No declarar dependencias productivas reales todavía. No publicar graph en `UnifiedRuntimeObservability` ni Analysis Mode. No crear manager/registry/graph paralelo. No inferir dependencias por imports/wiring/nombres/tests/scans. No abrir episodes/budgets, versions, certifications ni G5-R4. No activar diagnostics, Reasoning, Planning, Reflection, Memory, Learning, recovery o autonomía automáticamente.
