# ROBY XI.2 — GATE 4.A.1 — Existing UnifiedRuntimeObservability → Read-Only Introspection Projection Extension — SURGICAL GREEN

## Tipo
SURGICAL GREEN arquitectónico.

## Baseline de entrada
CONTRACT RED certificado localmente por el usuario: **7 FAIL contractuales esperados + 13.968 PASS + Ruff limpio + 0 fallos externos**.

## Objetivo
Cerrar exclusivamente el contrato RED de GATE 4.A.1 extendiendo la superficie oficial existente `app.unified_runtime_observability.UnifiedRuntimeObservability` con proyecciones introspectivas explícitas, read-only y subordinadas.

No se crea una nueva autoridad de introspección. `OfficialRuntime.observability(...)` permanece como entrada oficial.

## Cambios productivos

### `app/unified_runtime_observability.py`
Se agregan únicamente proyecciones read-only sobre estado ya existente:

1. `capability_registry`
   - consume `OfficialRuntimeCapabilityRegistry.interface_snapshot()` cuando está disponible;
   - conserva los `RuntimeCapabilityView` existentes;
   - no registra, ejecuta, habilita ni deshabilita capacidades.

2. `self_model`
   - se obtiene exclusivamente de `cognitive_core_runtime.snapshot.state.self_model` ya publicado;
   - si no existe core/estado/self-model, devuelve `None`;
   - no ejecuta evaluación ni ciclo cognitivo.

3. `reflection`
   - agrega `ReflectionObservabilitySnapshot`;
   - `architecture` proviene de `CanonicalReflectionFacade().snapshot`;
   - `published_state` proviene únicamente del estado ya publicado por el cognitive core;
   - no se llama `reflect(...)` ni se requiere binding.

4. `self_diagnostics`
   - agrega `SelfDiagnosticsObservabilitySnapshot`;
   - expone `GovernedSelfDiagnostics.AUTHORITY_ID`;
   - declara `implemented=True`;
   - declara `runtime_provisioned=False`;
   - `current_report=None`;
   - no ejecuta `diagnose(...)` ni fabrica reporte.

## Test contractual corregido por el usuario
Se integra en esta entrega el archivo corregido por el usuario:

`tests/architecture/test_gate4a1_existing_unified_runtime_observability_introspection_projection_contract_red.py`

Las correcciones son exclusivamente de formato/imports del contrato RED y se preservan en la entrega GREEN.

## Autoridades preservadas
- `UnifiedRuntimeObservability` continúa siendo la única superficie raíz de observabilidad/introspección.
- `OfficialRuntimeCapabilityRegistry` continúa siendo la autoridad de capabilities.
- Cognitive Core/Self Model continúa siendo la autoridad de estado cognitivo.
- `CanonicalReflectionFacade` sólo aporta metadata estructural; no se crea segunda autoridad de Reflection.
- `GovernedSelfDiagnostics` continúa siendo la autoridad diagnóstica; no se provisiona ni ejecuta un nuevo diagnóstico en observability.

## STOP preservado
No se autoriza:
- `AnalysisModeManager`;
- `IntrospectionManager`;
- segundo registry;
- segundo Self Model;
- segundo diagnostics engine;
- segundo reflection authority;
- `reflect(...)` desde observability;
- `diagnose(...)` desde observability;
- Memory/Learning writes;
- Planning N+1;
- ejecución/reparación;
- background introspection;
- chain-of-thought;
- modificación de `.roby/config.json`.

`credencial.json`, si existe, debe permanecer preservado.

## Validación del entorno de integración
Validación focal ejecutada después del GREEN:

```text
16 passed
```

Incluye el contrato GATE 4.A.1 y los contratos históricos de `UnifiedRuntimeObservability`.

La suite integral y Ruff quedan pendientes de certificación local del usuario; no se declaran como ejecutados en este entorno.

## Estado
**GATE 4.A.1 — SURGICAL GREEN IMPLEMENTADO / PENDIENTE DE CERTIFICACIÓN LOCAL INTEGRAL.**
