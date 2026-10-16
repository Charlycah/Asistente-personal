# ROBY XI.2 — LEGACY ROBY RUNTIME RETIREMENT REVIEW

## Estado
INSPECTION ONLY — NO CODE OR TESTS MODIFIED

Baseline certificado de entrada:
14.139 PASS · 0 FAIL · Ruff clean.

## Objeto de revisión
`core/roby.py` — clase `ROBY`, actualmente registrada como:

- key: `legacy_roby_runtime`
- target: `core.roby:ROBY`
- disposition: `LEGACY_ISOLATED`
- executable: `False`
- delegates_to: `None`

El runtime oficial actual es:
`app.official_runtime_composition:OfficialROBYRuntime`.

---

## 1. Consumidores reales de `core.roby`

Barrido de código productivo:

### Consumidores productivos
**0**

No hay imports de `core.roby` en:
- `app/`
- `application/`
- `domain/`
- `infrastructure/`
- `interfaces/`
- `scripts/`
- `main.py`

No hay entrypoint, builder, bootstrap, adapter productivo ni Composition Root que
construya `core.roby.ROBY`.

### Referencias restantes
Sólo:
- `app/runtime_compatibility.py`
- `tests/architecture/test_m395_4_compatibility_legacy.py`
- tres archivos históricos de tests:
  - `tests/test_m17_event_publisher.py`
  - `tests/test_m19_memory_pipeline.py`
  - `tests/test_m21_persistent_memory.py`
- documentación histórica/actual.

Conclusión:
`core.roby` no tiene reachability productiva.

---

## 2. Naturaleza del archivo

`core/roby.py` tiene aproximadamente 180 líneas.

Compone directamente:
- M4 `DecisionEngine`
- M5 `ExecutionEngine`
- M5 `ExecutionRegistry`
- M6 `ResponseLayer`
- M7 `ConversationController`
- M7 `SessionManager`
- event publisher
- observability
- tracing
- legacy memory pipeline
- cache

Esto constituye un runtime histórico completo, aunque aislado.

Su existencia ya no aporta una capability vigente.
Tampoco actúa como thin alias ni delega al runtime oficial.

Por tanto es una implementación paralela físicamente presente, aunque
arquitectónicamente desautorizada.

---

## 3. Justificación histórica actual

El propio registro de compatibilidad dice:

> “Runtime histórico congelado. Conservado sólo por compatibilidad y pruebas;
> nunca es un root oficial de ejecución.”

La revisión no encontró consumidores que ejerzan esa compatibilidad.

La justificación actual es circular:

`core.roby` se conserva porque existen tests
→ los tests permanecen porque `core.roby` existe.

Esto dejó de ser una razón arquitectónica suficiente después de Group A.

Además, el documento M246 ya incluía explícitamente:

`historical core.roby.ROBY compatibility retirement`

como integración diferida.

El retiro estaba, por tanto, previsto históricamente y no representa una nueva
dirección improvisada.

---

## 4. Tests aún dependientes de `core.roby`

Quedan exactamente cinco tests conductuales que construyen `ROBY()`.

### M17
`test_roby_process_publishes_trace_and_telemetry_events_through_event_publisher`

El mismo archivo conserva tres tests independientes de:
- CompositeEventPublisher
- TraceEventSubscriber
- TelemetryEventSubscriber

La capacidad base M17 no depende de `core.roby`.

### M19
Tres tests:
- successful turn captured in memory
- no response captured when resolution fails
- memory capture failure does not fail ROBY

El mismo archivo conserva tests directos del `StoreBackedMemoryPipeline`.

La capacidad de memory pipeline permanece testable sin `core.roby`.

### M21
Un test:
- `test_roby_can_capture_turns_in_sqlite_memory_store`

Los otros cuatro tests certifican directamente `SQLiteMemoryStore`.

La persistencia M21 permanece testable sin `core.roby`.

### Conclusión
Los cinco tests son integration certification específica del runtime legacy.
No son la única cobertura de M17/M19/M21.

Clasificación:
**RETIRE WITH RUNTIME**

No es necesario borrar completos esos tres archivos; sólo retirar:
- imports de `core.roby`
- los cinco tests que construyen `ROBY()`.

---

## 5. M395.4 después del retiro

El guardrail actual espera:

- HAL = RETIRED
- ROBY = LEGACY_ISOLATED
- `core/roby.py` existe implícitamente
- `core/roby.py` es el único importer permitido M3→M7 desde `core/`.

Si se retira `core.roby`, M395.4 debe evolucionar de forma natural:

### `legacy_roby_runtime`
- target sigue `core.roby:ROBY` sólo como identificador histórico;
- disposition → `RETIRED`
- executable = `False`
- delegates_to = `None`
- assert `core/roby.py` does not exist.

### Import boundary
`ALLOWED_CORE_LEGACY_IMPORTERS` pasa de:
`{"core/roby.py"}`

a:
`set()`

y el contrato debe exigir que ningún archivo de `core/` importe M3→M7.

Esto fortalece la arquitectura.

---

## 6. ¿Debe retirarse M3→M7 junto con `core.roby`?

**NO.**

El retiro de `core.roby` y el retiro de M3→M7 son decisiones diferentes.

M3→M7:
- están registrados como frozen legacy packages;
- tienen dependencias internas históricas;
- poseen tests propios;
- M6 `response.models` sigue siendo shim hacia `domain.response`;
- contratos posteriores todavía verifican algunas superficies canónicas legacy.

Por tanto:

`core.roby` puede retirarse sin eliminar M3→M7.

Después del retiro, M3→M7 quedan todavía más claramente como:
**historical frozen packages without runtime root**.

Su eventual reducción debe hacerse en otra reconciliación.

---

## 7. Riesgo de retiro de `core.roby`

### Riesgo productivo
**MUY BAJO**

Razón:
0 consumidores productivos.

### Riesgo de tests
**BAJO**

Sólo 5 tests conductuales necesitan retiro puntual.
Los componentes que esos tests tocaban conservan cobertura directa.

### Riesgo arquitectónico
**POSITIVO / REDUCCIÓN DE RIESGO**

Eliminar `core.roby`:
- elimina un runtime histórico completo;
- elimina el único importer M3→M7 desde `core/`;
- reduce la posibilidad de reactivación accidental de una segunda ruta;
- alinea estado físico con `executable=False`;
- acerca `LEGACY_ISOLATED` a `RETIRED`.

---

## 8. Cirugía aprobable

La futura implementación debe limitarse a:

1. eliminar `core/roby.py`;
2. cambiar `legacy_roby_runtime`:
   - `LEGACY_ISOLATED` → `RETIRED`;
3. actualizar M395.4:
   - afirmar ausencia de `core/roby.py`;
   - `ALLOWED_CORE_LEGACY_IMPORTERS = set()`;
   - exigir cero importers M3→M7 desde `core/`;
4. retirar sólo cinco tests `ROBY()`:
   - 1 de M17
   - 3 de M19
   - 1 de M21
5. conservar los restantes tests de esos archivos;
6. actualizar Current Truth / validation documentation;
7. NO tocar:
   - M3→M7
   - `m6.response.models`
   - `app.ui_adapter`
   - `app.runtime_ui_adapter`
   - Composition Root
   - OfficialROBYRuntime
   - memory authorities/stores actuales
   - persistence productiva.

---

## 9. Efecto esperado sobre pytest

Baseline:
14.139

Retiro directo estimado:
5 tests

Baseline esperado preliminar:
**14.134**

Este número debe considerarse sólo una predicción.
La certificación real la define la suite completa.

---

## 10. Decisión final

# LEGACY ROBY RUNTIME RETIREMENT — APPROVED FOR IMPLEMENTATION

Confianza:
**ALTA**

Razones centrales:

1. no tiene consumidores productivos;
2. no es alias del runtime oficial;
3. no es una autoridad vigente;
4. está marcado `executable=False`;
5. su única justificación actual son pruebas/compatibilidad no ejercida;
6. M246 ya documentaba su retiro como deuda diferida;
7. sólo cinco tests siguen vinculados directamente;
8. retirar el runtime fortalece el boundary M3→M7;
9. M3→M7 pueden preservarse sin ese root;
10. no requiere tocar ninguna autoridad productiva.

## Próximo paso recomendado

**LEGACY ROBY RUNTIME RETIREMENT — IMPLEMENTATION**

Cirugía pequeña, explícita y reversible por historia documental.
