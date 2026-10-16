# ROBY XI.2 — GATE 4.A.1 — Existing UnifiedRuntimeObservability → Read-Only Introspection Projection Extension — CONTRACT RED

## Tipo
CONTRACT RED arquitectónico. Sin cambios productivos.

## Baseline de entrada
GATE 4.A certificado por el usuario: **13.963 PASS + Ruff limpio + 0 FAIL**.

## Objetivo
Congelar contractualmente la extensión mínima de `app.unified_runtime_observability.UnifiedRuntimeObservability` para exponer introspección read-only reutilizando exclusivamente las autoridades existentes.

No se crea una nueva autoridad de introspección. `OfficialRuntime.observability(...)` continúa siendo la entrada oficial y `UnifiedRuntimeObservability` continúa siendo la única superficie raíz de proyección.

## Contrato RED fijado
El archivo contractual es:

`tests/architecture/test_gate4a1_existing_unified_runtime_observability_introspection_projection_contract_red.py`

El RED exige cuatro proyecciones explícitas sobre el snapshot unificado existente:

1. `capability_registry`
   - debe provenir de `OfficialRuntimeCapabilityRegistry.interface_snapshot()`;
   - debe conservar `RuntimeCapabilityView` inmutable;
   - no debe registrar, ejecutar ni alterar capacidades.

2. `self_model`
   - debe provenir exclusivamente de `cognitive_core_runtime.snapshot.state.self_model` ya publicado;
   - si no hay core/estado/self-model, debe ser `None`;
   - no debe ejecutar `CognitiveSelfModel.assess(...)`.

3. `reflection`
   - debe exponer metadata estructural de `CanonicalReflectionFacade.snapshot`;
   - puede exponer únicamente `reflection` ya publicada por el cognitive core;
   - no debe ejecutar `reflect(...)`, bindear silenciosamente la facade ni exponer chain-of-thought.

4. `self_diagnostics`
   - debe declarar la autoridad existente `GovernedSelfDiagnostics.AUTHORITY_ID`;
   - debe declarar honestamente que no existe runtime/current-report provisionado en este gate;
   - `current_report` debe permanecer `None`;
   - observability no debe ejecutar `diagnose(...)`.

## RED esperado
Validación focal del contrato sobre la producción aún no extendida:

```text
7 failed, 5 passed
```

Los siete fallos esperados corresponden exclusivamente a las superficies todavía ausentes:
- campos introspectivos explícitos aún no presentes en `UnifiedRuntimeObservabilitySnapshot`;
- `interface_snapshot()` aún no consumido;
- Self Model aún no proyectado explícitamente;
- Reflection aún no proyectada explícitamente;
- Self Diagnostics aún no proyectado explícitamente.

Los cinco invariantes que ya pasan congelan los límites existentes:
- observability no llama `reflect(...)` ni `diagnose(...)`;
- `OfficialRuntime.observability(...)` sigue siendo la entrada oficial;
- no se crea autoridad paralela de introspección/análisis;
- `CanonicalReflectionFacade.snapshot` sigue siendo estructural y no requiere binding;
- `.roby/config.json` permanece byte-identical respecto de la baseline certificada de GATE 4.A.

## Frontera de implementación GREEN posterior
El GREEN, si el usuario certifica este RED, debe ser quirúrgico y quedar centrado en `app/unified_runtime_observability.py`, salvo que una dependencia estrictamente necesaria sea demostrada por el contrato.

No autoriza:
- `AnalysisModeManager`;
- `IntrospectionManager`;
- segundo registry;
- segundo Self Model;
- segundo diagnostics engine;
- segundo reflection authority;
- ejecución de diagnostics o reflection desde observability;
- Memory/Learning writes;
- Planning N+1;
- ejecución/reparación;
- background introspection;
- chain-of-thought.

## STOP
No se implementa GREEN antes de la certificación local del RED esperado.

## Estado
**GATE 4.A.1 — CONTRACT RED PREPARADO / PENDIENTE DE CERTIFICACIÓN LOCAL.**
