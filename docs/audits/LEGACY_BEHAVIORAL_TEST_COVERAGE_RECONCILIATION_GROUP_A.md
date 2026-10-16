# ROBY XI.2 — LEGACY BEHAVIORAL TEST COVERAGE RECONCILIATION — GROUP A

## Estado
INSPECTION / RECONCILIATION ONLY  
NO TESTS MODIFIED OR REMOVED

Baseline:
14.191 PASS · 0 FAIL · Ruff clean

## Alcance
Se reconciliaron exclusivamente estos seis archivos:

1. `tests/test_hal_end_to_end.py`
2. `tests/test_hal_public_api.py`
3. `tests/test_hal_observability.py`
4. `tests/test_hal_tracing.py`
5. `tests/test_m18_hal_memory_integration.py`
6. `tests/test_m22_hal_cache_integration.py`

Contienen:
- 49 funciones `test_*`
- 1 test parametrizado con 4 variantes
- 52 casos pytest estimados en total

## Principio de decisión

`core.roby` permanece oficialmente `LEGACY_ISOLATED`.

Por tanto, ya no es necesario mantener tests positivos destinados a demostrar que
ese runtime histórico conserva todas sus capacidades antiguas, siempre que:

- los componentes internos relevantes tengan cobertura independiente;
- el runtime moderno tenga cobertura equivalente para la capacidad vigente;
- el guardrail de aislamiento histórico permanezca activo.

Ese guardrail es M395.4 y NO forma parte del Group A.

---

## 1. `test_hal_end_to_end.py`

### Cobertura histórica
9 tests.

Certifica:
- M3 intent parsing;
- M4 planning;
- M5 execution;
- M6 response building;
- `core.roby.ROBY.process`;
- reminder success / missing information / failure;
- no exposición directa de ExecutionResult.

### Cobertura sustituta
- M3/M4/M5/M6 conservan tests unitarios y de integración propios.
- La conversación productiva actual está cubierta por M253/M256/M265 y posteriores.
- El entry/runtime oficial ya no es `core.roby`.

### Decisión
**RETIRE CANDIDATE — HIGH CONFIDENCE**

No protege un boundary actual.
Es certificación positiva de un pipeline legacy.

---

## 2. `test_hal_public_api.py`

### Cobertura histórica
17 funciones; una parametrizada en 4 variantes.
20 casos pytest estimados.

Certifica:
- API pública de `ROBY.process`;
- creación/reutilización de session;
- pending plans;
- missing information;
- cancelación;
- confirmation/rejection;
- session scoping.

### Cobertura sustituta
- M7 conserva contratos propios de session/conversation state.
- La conversación productiva actual está cubierta por:
  - M253 Conversation Runtime
  - M256 Conversation Entry Runtime
  - M265 Official Conversation Execution Integration
  - capas posteriores de continuidad/contexto/conversación.
- `core.roby` ya no es entrypoint oficial.

### Decisión
**RETIRE CANDIDATE — HIGH CONFIDENCE**

Mantener este archivo equivale a exigir que una API legacy aislada siga funcionando
como una API vigente.

---

## 3. `test_hal_observability.py`

### Cobertura histórica
6 tests.

Certifica:
- request_started/completed/failed;
- counters legacy;
- history before failure;
- observabilidad alrededor del flujo `ROBY.process`.

### Cobertura sustituta
- M17 certifica EventPublisher y secuencia de eventos.
- M269 certifica Conversation Reliability Observability productiva.
- RP18.6 certifica UnifiedRuntimeObservability como superficie oficial única.

### Decisión
**RETIRE CANDIDATE — HIGH CONFIDENCE**

La observabilidad vigente tiene una autoridad y contratos posteriores mucho más
fuertes. Mantener observabilidad positiva de `core.roby` no aporta protección
arquitectónica actual.

---

## 4. `test_hal_tracing.py`

### Cobertura histórica
11 tests.

Certifica:
- secuencia:
  `roby.process.started → session → conversation → execution → response → completed`;
- terminal completed/failed;
- ordering invariants;
- no response después de execution failure.

### Cobertura sustituta
- M17 ya certifica los eventos del pipeline histórico como componente/event model.
- M181 y superficies posteriores cubren operational trace.
- M269/RP18.6 cubren observabilidad/tracing productivo actual.
- El pipeline oficial moderno no depende de `core.roby`.

### Decisión
**RETIRE CANDIDATE — HIGH CONFIDENCE**

Es behavioral tracing de una isla legacy, no tracing del runtime oficial.

---

## 5. `test_m18_hal_memory_integration.py`

### Cobertura histórica
3 tests.

Certifica:
- `ROBY()` usa NullMemoryStore por defecto;
- acepta memory store inyectado;
- `ROBY.process` captura user_input/user_response.

### Cobertura sustituta
- `test_m18_memory_abstraction.py` certifica NullMemoryStore.
- `test_m19_memory_pipeline.py` certifica capture de user_input/user_response y
  tolerancia a fallos.
- capas M36+ y canonical memory posterior certifican memoria cognitiva vigente.
- la integración legacy dentro de `core.roby` ya no es productiva.

### Decisión
**RETIRE CANDIDATE — HIGH CONFIDENCE**

No retirar los tests M18/M19 de los componentes; sólo este integration wrapper
legacy.

---

## 6. `test_m22_hal_cache_integration.py`

### Cobertura histórica
3 tests.

Certifica:
- `ROBY()` usa InMemoryCacheStore;
- acepta cache inyectado;
- `ROBY.process` no modifica una entrada cache preexistente.

### Cobertura sustituta
- `test_m22_cache.py` certifica directamente CacheEntry/InMemoryCacheStore:
  get/set/overwrite/delete/clear.
- el runtime oficial moderno no depende de `core.roby` como cache integration
  boundary.

### Decisión
**RETIRE CANDIDATE — HIGH CONFIDENCE**

La única parte exclusiva es el wiring legacy de `core.roby`, que ya no necesita
certificación positiva.

---

# Matriz final

| Archivo | Casos aprox. | Clasificación |
|---|---:|---|
| `test_hal_end_to_end.py` | 9 | RETIRE |
| `test_hal_public_api.py` | 20 | RETIRE |
| `test_hal_observability.py` | 6 | RETIRE |
| `test_hal_tracing.py` | 11 | RETIRE |
| `test_m18_hal_memory_integration.py` | 3 | RETIRE |
| `test_m22_hal_cache_integration.py` | 3 | RETIRE |
| **TOTAL** | **52** | **RETIRE CANDIDATE** |

## Contratos que deben permanecer

NO retirar:
- `tests/architecture/test_m395_4_compatibility_legacy.py`
- tests propios de M3→M7 por esta cirugía
- `test_m17_event_publisher.py`
- `test_m18_memory_abstraction.py`
- `test_m19_memory_pipeline.py`
- `test_m22_cache.py`
- M253/M256/M265
- M269
- RP18.6 Unified Observability
- contratos modernos de memory/conversation/architecture

## Efecto esperado si se implementa

Como el Group A representa 52 casos pytest estimados:

Baseline actual:
`14.191`

Baseline esperado después del retiro:
`14.139`

Esto es una estimación estructural previa a la ejecución oficial; el número
definitivo sólo se certifica con pytest completo.

## Riesgo
BAJO.

Razones:
- no se modifica código productivo;
- no se elimina el guardrail M395.4;
- cada capacidad relevante conserva cobertura independiente/moderna;
- sólo se retira certificación positiva de una runtime island declarada
  `LEGACY_ISOLATED`.

## Conclusión

**GROUP A — RECONCILED**

Los seis archivos pueden avanzar juntos a una primera cirugía de reducción.

Recomendación:
`LEGACY BEHAVIORAL TEST RETIREMENT — GROUP A IMPLEMENTATION`

La implementación debe:
1. borrar únicamente estos seis archivos;
2. registrar documentalmente que su cobertura fue superseded;
3. no modificar tests modernos para “compensar” artificialmente el retiro;
4. ejecutar tests dirigidos de replacements;
5. ejecutar:
   - clean_project_caches
   - generate_quality_baseline
   - ruff check .
   - pytest -q

Resultado esperado preliminar:
**14.139 PASS · 0 FAIL · Ruff clean**
