# Mobile + Driving Legacy Executable Lineage Retirement — Validation Record

## Status

**IMPLEMENTED / PENDING OWNER CERTIFICATION**

Input certified baseline: **13,746 PASS · 0 FAIL · Ruff clean**.

## Retired executable surface

- `app/driving_runtime.py`
- `core/mobile_companion/`
- `core/mobile_runtime/`
- `core/mobile_presence/`
- `core/notification_intelligence/`
- `core/background_continuity/`
- `core/mobile_context/`
- `core/hands_free/`
- `core/driving_companion/`
- `core/driving_context/`
- `core/driving_interaction_policy/`
- `core/driving_conversation_adaptation/`
- `core/driving_safety_coordination/`
- `core/mobile_extension/`

## Retired positive tests

`tests/test_m110_mobile_companion_foundation.py` through `tests/test_m121_driving_safety_coordination.py`, plus `tests/test_m259_driving_runtime.py` and `tests/test_rp249_mobile_extension.py`: **461 test functions / 541 collected Pytest cases** from the retired object.

## Reconciled current contracts

- `app/runtime_root_factory.py`: removed Driving import, construction, registration and dependency wiring.
- `app/end_to_end_conversation_runtime.py`: removed passive Driving dependency; integrated runtime count 8 → 7.
- `core/runtime_composition_root/models.py`: removed obsolete `driving_runtime` slot.
- M247, M264 and M387.5: surgically reconciled, otherwise preserved.
- M396.3 authority-preservation manifest: only the deliberately changed Composition Root hash was refreshed. Historical manifests remain untouched.

## Preserved boundaries

`OfficialDeviceRuntimeGateway`, `core/device_capabilities/`, `core/device_continuity/`, Presence, multimodal, reasoning, memory, current Composition Root authority, historical milestone/ADR documentation and historical SHA manifests remain preserved.

## Handoff rule

This snapshot contains physical deletions. **Do not overlay it onto an existing HAL directory.** Validate from a clean extraction and restore the owner's private `.roby` state locally before running the full suite. `.roby`, credentials, caches and bytecode are excluded from the package.

Owner certification sequence:

```powershell
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

## Local implementation evidence

- Full Pytest collection on the clean candidate snapshot: **13,209 collected tests**.
- Arithmetic reconciliation: **13,746 certified input − 541 retired collected cases + 4 new guardrails = 13,209**.
- Focused current-contract validation: **91 passed** across Device capability registry, M247, M264, M387.5, M396.3/4/5 and retirement guardrails.
- Container environment does not provide the project Ruff executable; official Ruff and full-suite certification remain owner responsibilities.
