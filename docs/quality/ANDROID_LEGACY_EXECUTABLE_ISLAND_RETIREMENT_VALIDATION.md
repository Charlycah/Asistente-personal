# Android Legacy Executable Island Retirement — Validation

## State

**IMPLEMENTED / PENDING OWNER CERTIFICATION**

Certified input baseline: **13.912 PASS · 0 FAIL · Ruff clean**.

## Governed scope

This surgery materializes the current laptop-only direction by retiring only the proven Android executable island and its Android-backed Current Location implementation. It does not retire the neutral M364 device foundation or the modern laptop `OfficialDeviceRuntimeGateway`.

## Retired productive files

- `app/android_bridge.py`
- `core/android_bridge/`
- `core/android_device_state.py`
- `core/android_notifications.py`
- `core/android_clipboard.py`
- `core/android_files.py`
- `core/android_sensors.py`
- `core/android_location.py`
- `core/current_location/`

`app/device_gateway.py` remains and has only its Android-specific imports, in-memory state, and observe/latest methods removed.

## Test reconciliation

Thirteen Android/current-location positive certification files were retired: M365.1→M365.7, M370.1, M371, M372, M373, M374 and M399.1. They contained exactly **170 tests**. The obsolete Android-path assertion was removed from the surviving M395.1 neutral-boundary test. M364, M394 and M396 contracts remain.

`tests/architecture/test_android_legacy_retirement.py` adds four guardrails covering physical absence, no Android extension on the neutral M364 gateway, preservation of `OfficialDeviceRuntimeGateway`, and absence of Android dependencies from the Runtime Root.

Expected collection before owner certification: approximately **13.746 tests**.

## Explicit non-scope

No change is authorized here to Mobile, Driving, Residential/MINI-PC, Composition Root behavior, ToolGateway, persistence, Memory, Learning, cognition, current authorities, or private `.roby` state. Historical Android documentation remains evidence and is not deleted.

## Local implementation validation

- Focused preserved-contract suite (M364 + M394 + M395.1 + M396 + retirement guardrails): **132 PASS**.
- All surviving tests that reference `OfficialDeviceGateway` / `app.device_gateway`: **124 PASS**.
- Productive `app/` + `core/` search after surgery: **0 Android imports / 0 `observe_android_*` / 0 `latest_android_*` references**.
- Full-suite certification could not be completed in the packaging container because the repository ZIP intentionally excludes private `.roby/config.json`; Gate4A1 reads that owner-local file during test collection. A second broad run excluding that environmental test advanced without an Android failure but exceeded the container execution limit.
- Ruff is not installed in the packaging container, so Ruff certification remains owner-only for this handoff.

These limitations do not promote the surgery. State remains **IMPLEMENTED / PENDING OWNER CERTIFICATION**.

## Owner certification

Run exactly:

```powershell
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

Only the owner result may promote this surgery to **CLOSED / CERTIFIED**.
