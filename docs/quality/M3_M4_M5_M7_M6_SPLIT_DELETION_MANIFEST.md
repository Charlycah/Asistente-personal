# ROBY XI.2 — M3/M4/M5/M7 + M6 SPLIT DELETION MANIFEST

This manifest exists because extracting a ZIP over an existing Windows project does not delete stale files.

## Retired package trees
- `m3/`
- `m4/`
- `m5/`
- `m7/`

## Retired M6 runtime files
- `m6/response/response_layer.py`
- `m6/response/renderers.py`

## Retired/superseded root tests
- `tests/test_m4_context.py`
- `tests/test_m4_decision_engine.py`
- `tests/test_m4_models.py`
- `tests/test_m5_execution_engine.py`
- `tests/test_m5_execution_registry.py`
- `tests/test_m5_reminder_integration.py`
- `tests/test_m6_response_layer.py`
- `tests/test_m20_tool_system.py`
- `tests/test_rp_20_14_forwarding_module_cleanup.py`

## Archived active migration scripts
These must no longer remain under `scripts/migrations/`:
- `APPLY_RP_20_14.ps1`
- `APPLY_RP_20_15.ps1`

Historical copies live under `docs/history/migrations/`.

## Must remain
- `m6/response/__init__.py`
- `m6/response/models.py`
