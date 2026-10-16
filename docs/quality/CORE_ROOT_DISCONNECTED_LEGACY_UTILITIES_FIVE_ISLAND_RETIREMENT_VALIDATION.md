# ROBY XI.2 — Core root disconnected legacy utilities five-island retirement

## Scope

Governed physical retirement of five disconnected historical root utilities:

- `core/circuit_breaker.py`
- `core/retry.py`
- `core/event_bus.py`
- `core/logging.py`
- `core/runtime.py`

`core/cache.py` is explicitly excluded and preserved.

## Audit basis

Before implementation, each retired file had:

- zero productive direct imports;
- zero exact dynamic imports;
- zero current-authority documentary contracts;
- no Composition Root ownership;
- no persistence, writer, store or capability authority;
- no active direct tests requiring the file.

Historical SHA entries remain under `docs/history/manifests/SHA256SUMS.txt` and
are intentionally not rewritten.

## Preserved current surfaces

- `core.cache.InMemoryCacheStore`
- `core.cognitive_event_bus.CognitiveEventBus`
- `core.executive_recovery_health.RecoveryHealthCoordinator`
- `core.runtime_composition_root.RuntimeCompositionRoot`

## Guardrail

`tests/architecture/test_core_root_disconnected_legacy_utilities_retirement.py`
asserts absence of the five retired paths and preservation of the four current
surfaces above.

## Certification state

**IMPLEMENTED / PENDING OWNER CERTIFICATION**

Expected owner baseline after one new guardrail:
**12,537 PASS · 0 FAIL · Ruff clean**.

Owner gate:

```powershell
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```
