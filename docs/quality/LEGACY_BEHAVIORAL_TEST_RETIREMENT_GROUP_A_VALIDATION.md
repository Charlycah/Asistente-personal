# Legacy Behavioral Test Retirement — Group A — Validation Status

Baseline de partida: **14,191 PASS · 0 FAIL · Ruff clean**.

## Scope

Retired from the active pytest suite:

- `tests/test_hal_end_to_end.py`
- `tests/test_hal_public_api.py`
- `tests/test_hal_observability.py`
- `tests/test_hal_tracing.py`
- `tests/test_m18_hal_memory_integration.py`
- `tests/test_m22_hal_cache_integration.py`

These files positively certified behavior of the historical `core.roby` runtime island. `core.roby` remains `LEGACY_ISOLATED`; the active architectural isolation guardrail remains `tests/architecture/test_m395_4_compatibility_legacy.py`.

No productive code was modified.

## Preserved replacement/current coverage

- event publication/component contracts: M17;
- memory abstraction/pipeline contracts: M18/M19 and later canonical memory contracts;
- cache component contracts: M22;
- productive conversation contracts: M253/M256/M265 and later conversation layers;
- productive observability/tracing: M269 / RP18.6 and later unified observability contracts;
- legacy isolation: M395.4.

## Expected collection delta

The reconciliation estimated 52 pytest cases in Group A. Therefore the preliminary expected full-suite total is approximately **14,139 PASS**. This is not a certification number; parametrization/collection behavior makes the owner-environment `pytest -q` result authoritative.

## Certification sequence

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

Status: **CLOSED / CERTIFIED**.

Owner-environment result: **14,139 PASS · 0 FAIL · Ruff clean**.
