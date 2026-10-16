# ROBY XI.2 — LEGACY ROBY RUNTIME RETIREMENT VALIDATION

## State
CLOSED / CERTIFIED

## Baseline input
14,139 PASS · 0 FAIL · Ruff clean.

## Productive change
- `core/roby.py` retired.
- `legacy_roby_runtime` changed from `LEGACY_ISOLATED` to `RETIRED`.
- No official runtime, Composition Root, authority, store, writer, persistence path, or M3→M7 package was changed.

## Test reconciliation
Five integration tests that instantiated the retired `ROBY()` runtime were removed surgically:
- M17: 1
- M19: 3
- M21: 1

Direct component coverage in M17, M19, and M21 remains. M395.4 now requires both historical HAL and ROBY runtimes to be absent and requires zero M3→M7 importers from `core/`.

## Owner certification
14,134 PASS · 0 FAIL · Ruff clean.

Construction-environment checks:
- structural retirement checks: PASS;
- focused boundary/component suite: 46 PASS · 0 FAIL;
- `pytest --collect-only -q`: 14,134 tests collected;
- `clean_project_caches.py`: PASS;
- `generate_quality_baseline.py`: PASS;
- Ruff unavailable in construction environment.

Owner full validation completed successfully; this retirement is certified closed.
