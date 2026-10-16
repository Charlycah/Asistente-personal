# ROBY XI.2 — M3/M4/M5/M7 LEGACY EXECUTABLE ISLAND RETIREMENT + M6 RESPONSE RUNTIME SPLIT

## State
IMPLEMENTED / PENDING OWNER CERTIFICATION

## Certified input baseline
14,134 PASS · 0 FAIL · Ruff clean.

## Productive retirement
- M3, M4, M5, and M7 executable package trees retired.
- M6 historical response layer and renderers retired.
- `m6.response.models` retained as identity-preserving shim to `domain.response`.
- No official runtime, Composition Root, authority, store, writer, persistence path, `domain.response`, or `core.tool_gateway` behavior changed.

## Test reconciliation
205 collected historical tests were reconciled with the retired island and removed/superseded. M395.1 remains; M395.4 was updated to guard the new retired-package state and the minimal M6 compatibility surface.

## Supporting hygiene
- M3/M4/M5/M7 removed from quality production roots.
- RP20.14 and RP20.15 one-shot migration scripts archived under `docs/history/migrations/`.

## First owner validation
13,924 PASS · 5 FAIL · Ruff clean.

All five failures were residual historical guardrails, not runtime regressions:
- four RP20.15 tests still required retired M4/M5 files or tests;
- one RP20.3 assertion still required retired M3/M4/M5/M7 compatibility files.

## FIX1 reconciliation
- `tests/test_rp_20_15_init_surface_cleanup.py` retired in full because all four contracts were superseded by physical retirement of M4/M5 and their historical tests.
- `tests/test_rp_20_3_orphan_module_removal.py` retained, but its compatibility-layer test now protects only maintained compatibility layers: `engines/memory_engine.py` and `m6/response/models.py`.

## Expected FIX1 owner baseline
13,925 PASS · 0 FAIL · Ruff clean.

## Construction-environment validation
- structural absence/reachability checks: PASS;
- `python -m compileall` on current production/test surfaces: PASS;
- `clean_project_caches.py`: PASS;
- `generate_quality_baseline.py`: PASS;
- focused architecture/runtime suite: **66 PASS · 0 FAIL**;
- original implementation collection excluding the local `.roby/config.json` contract: **13,917 collected**;
- owner validation proved the original total collection was **13,929**;
- FIX1 removes four superseded RP20.15 tests while preserving and repairing the RP20.3 compatibility guardrail, so expected FIX1 collection is **13,925**;
- full-suite construction run exceeded the execution limit before completion and showed no failure before interruption;
- Ruff is unavailable in the construction environment.

Final certification belongs to the owner's full validation sequence.
