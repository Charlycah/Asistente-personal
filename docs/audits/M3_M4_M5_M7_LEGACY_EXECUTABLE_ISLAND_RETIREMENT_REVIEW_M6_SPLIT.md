# ROBY XI.2 — M3/M4/M5/M7 LEGACY EXECUTABLE ISLAND RETIREMENT REVIEW
## + M6 RESPONSE RUNTIME SPLIT

### Estado
INSPECTION ONLY — NO CODE OR TESTS MODIFIED

Baseline certificado de entrada: **14.134 PASS · 0 FAIL · Ruff clean**.

## Decisión arquitectónica
La isla ejecutable histórica M3/M4/M5/M7 ya no tiene entrada desde el runtime oficial. Puede retirarse como una sola cirugía gobernada.

M6 requiere split: retirar `m6/response/response_layer.py` y `m6/response/renderers.py`, pero conservar `m6/response/models.py` y `m6/response/__init__.py`. El shim mantiene identidad con `domain.response` y sigue protegido por M395.1/M395.4.

**DECISIÓN: APPROVED FOR IMPLEMENTATION — HIGH CONFIDENCE.**

## Reachability final
- M3: 0 consumidores productivos modernos; sólo alimenta M4/M7 y tests históricos. RETIRE COMPLETE PACKAGE.
- M4: 0 consumidores productivos modernos; sólo M5/M7, tests y RP20.14. RETIRE COMPLETE PACKAGE.
- M5: 0 consumidores productivos modernos. `m5.tool_system` no es el sistema actual; `m5.registry` sólo permanece por importabilidad histórica. RETIRE COMPLETE PACKAGE.
- M7: 0 consumidores externos después de `core.roby`. RETIRE COMPLETE PACKAGE.
- M6: split. El response runtime es histórico; `m6.response.models` sigue siendo compatibilidad neutral.

## Código productivo/histórico a retirar
- M3: 10 archivos productivos, ~518 líneas, más `m3/intent_parser/tests/`.
- M4: 22 archivos productivos, ~1.049 líneas, más tests internos.
- M5: 7 archivos productivos, ~248 líneas.
- M7: 5 archivos productivos, ~108 líneas, más tests internos.
- M6 runtime: `response_layer.py` (37 líneas) y `renderers.py` (74 líneas).

Total: **46 archivos Python productivos/históricos**, ~**1.994 líneas**.

## Tests a retirar/supersede
La colección real confirmó **205 tests**:

### M3 internos — 31
- `m3/intent_parser/tests/test_classifier.py` — 8
- `m3/intent_parser/tests/test_entity_extractor.py` — 8
- `m3/intent_parser/tests/test_extractor.py` — 2
- `m3/intent_parser/tests/test_parser.py` — 4
- `m3/intent_parser/tests/test_text_normalizer.py` — 4
- `m3/intent_parser/tests/test_validator.py` — 5

### M4 internos — 122
- `m4/cognitive_scheduler/tests/test_scheduler.py` — 20
- `m4/cognitive_state/tests/test_state.py` — 10
- `m4/context_manager/tests/test_manager.py` — 8
- `m4/goal_manager/tests/test_goal_manager.py` — 14
- `m4/planning_layer/tests/test_planning_layer.py` — 21
- `m4/runtime/tests/test_runtime.py` — 21
- `m4/task_queue/tests/test_task_queue.py` — 24
- `m4/tests/test_decision_router.py` — 4

### M7 internos — 12
- `m7/tests/test_conversation_controller.py` — 4
- `m7/tests/test_session.py` — 4
- `m7/tests/test_session_manager.py` — 4

### Group B / externos — 30
- `tests/test_m4_context.py` — 2
- `tests/test_m4_decision_engine.py` — 9
- `tests/test_m4_models.py` — 3
- `tests/test_m5_execution_engine.py` — 4
- `tests/test_m5_execution_registry.py` — 4
- `tests/test_m5_reminder_integration.py` — 1
- `tests/test_m6_response_layer.py` — 7

### M20 — 6
- `tests/test_m20_tool_system.py` — 6

### RP20.14 — 4
- `tests/test_rp_20_14_forwarding_module_cleanup.py` — 4

Los 4 RP20.14 quedan superseded si M4/M5 desaparecen: no debe quedar un test exigiendo importabilidad de código retirado.

## Tests/guardrails que deben quedar
KEEP:
- `tests/architecture/test_m395_1_neutral_contract_boundaries.py`
- `tests/architecture/test_m395_4_compatibility_legacy.py` actualizado
- tests posteriores que importan `m6.response.models`
- tests de `domain.response`
- tests de `core.tool_gateway`
- tests del runtime oficial y adapters actuales.

## Runtime compatibility registry
No hace falta crear un modelo nuevo. Reutilizar `LegacyPackageRecord`:
- M3/M4/M5/M7: `frozen=False`, `modern_import_allowed=False`, role `retired_*`, notes de trazabilidad sin implementación física.
- M6: `frozen=True`, `modern_import_allowed=False`, role `response_compatibility_shim`, notes afirmando que sólo `m6.response.models` permanece.

## M395.4 debe certificar
1. `m3/`, `m4/`, `m5/`, `m7/` ausentes.
2. `m6/response/models.py` presente.
3. `m6/response/response_layer.py` y `renderers.py` ausentes.
4. M3/M4/M5/M7 records retired (`frozen=False`, roles `retired_*`).
5. M6 sigue frozen shim.
6. Cero imports modernos/core hacia M3/M4/M5/M7.
7. Cero imports del runtime moderno hacia `m6.response.models`.
8. Identidad `m6.response.models` == `domain.response` para `ResponseStatus` y `UserResponse`.

## M395.1
KEEP. Mantener la certificación de identidad neutral M6 y de ausencia de imports M6 en runtime moderno.

## Quality baseline
Hallazgo adicional: `scripts/generate_quality_baseline.py` todavía enumera M3/M4/M5/M6/M7 en `PRODUCTION_ROOTS`.
El script tolera raíces ausentes, pero el JSON seguiría declarando raíces ya retiradas. La implementación debe retirar M3/M4/M5/M7 de esa tupla y conservar sólo M6.

## Migration scripts
Hallazgo adicional:
- `scripts/migrations/APPLY_RP_20_14.ps1`
- `scripts/migrations/APPLY_RP_20_15.ps1`

leen rutas M4/M5 obligatoriamente y quedarían rotos tras el retiro.

Recomendación: **ARCHIVE, no mantener ejecutables activos**. Moverlos a una superficie histórica como `docs/history/migrations/` preserva la historia sin dejar scripts activos contra rutas inexistentes.

`APPLY_RP_20_12.ps1` menciona M5 pero tolera su ausencia; no es requisito de esta cirugía.

## Current Truth
El ZIP de inspección todavía refleja `core.roby` como pending owner certification. Antes de la nueva cirugía debe sincronizarse con el estado real:

**LEGACY ROBY RUNTIME RETIREMENT — CLOSED / CERTIFIED — 14.134 PASS · 0 FAIL · Ruff clean**.

Luego registrar esta nueva cirugía como `IMPLEMENTED / PENDING OWNER CERTIFICATION` hasta la suite completa.

## Efecto esperado
Baseline: 14.134.
Tests reconciliados: 205.
Estimación por colección: **13.929**.

Resultado esperado tras implementación/certificación: **~13.929 PASS · 0 FAIL · Ruff clean**.

## Exclusiones estrictas
NO tocar:
- `domain.response`
- `core.tool_gateway`
- OfficialROBYRuntime
- Composition Root
- current conversation runtime
- memory authorities/stores/persistence
- Android capabilities
- current adapters
- propósito de M395.1
- identidad de `m6.response.models`
- historia documental salvo notas de supersession/current truth.

No crear ningún manager, registry, store, writer, runtime, adapter o autoridad nuevos.

## Lista mínima de cirugía aprobada
1. eliminar `m3/`, `m4/`, `m5/`, `m7/`;
2. eliminar `m6/response/response_layer.py` y `renderers.py`;
3. conservar `m6/response/models.py` y package surface mínima;
4. retirar los 205 tests reconciliados;
5. actualizar `LEGACY_PACKAGE_REGISTRY`;
6. actualizar M395.4;
7. mantener M395.1;
8. actualizar `generate_quality_baseline.py`;
9. archivar RP20.14/RP20.15 migration scripts;
10. sincronizar Current Truth/quality validation docs;
11. validar cleanup, baseline, Ruff y pytest completo.

# DECISIÓN FINAL

**M3/M4/M5/M7 LEGACY EXECUTABLE ISLAND RETIREMENT + M6 RESPONSE RUNTIME SPLIT — APPROVED FOR IMPLEMENTATION.**

Debe retirarse M3/M4/M5/M7 completos, el runtime histórico M6 de respuesta, 205 tests reconciliados y la ejecución activa de RP20.14/RP20.15. Deben conservarse el shim `m6.response.models`, M395.1, M395.4 actualizado, `domain.response`, `core.tool_gateway`, el runtime oficial y toda la historia documental.
