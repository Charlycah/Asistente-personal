# M395.1 — Validation Report

## Base

- Predecessor: M394.8
- Declared predecessor suite: 10,299 tests
- Scope: neutral boundaries and contracts only

## Structural migrations

- `CameraFrame` -> `domain.vision.camera_frame`
- Cognitive Agenda contracts/models -> `domain.cognitive_agenda`
- Priority Reasoning -> `domain.priority_reasoning`
- Android activation device lookup -> `domain.device_gateway_contract.RegisteredDeviceLookup`
- Modern response contract -> `domain.response`
- Historical imports preserved through identity-compatible reexports/shims

## Dependency invariants

Confirmed absent after M395.1:

- `core -> app.priority_reasoning`
- `core -> app.device_gateway`
- `infrastructure -> app.cognitive_agenda_manager`
- `core -> infrastructure.camera.camera_client.CameraFrame`
- modern runtime -> `m6.response.models`

Historical `core.hal`, `core.roby` and `m7` retain the M6 response shim intentionally.

## Tests

M395.1 adds 8 architecture invariants.

`pytest --collect-only -q` after the change reports **10,307 tests**.

Because a single full-suite process exceeds the execution window of the audit container, the default pytest collection was executed in disjoint file blocks. Combined result for the default collection:

- **10,307 passed**
- **0 failed**

An additional live Gmail acceptance test that is outside the default pytest collection was accidentally included in one block and skipped; it is not part of the 10,307 default tests above.

## Static checks

- `python -m compileall` over production packages: clean.
- M395.1 forbidden dependency grep checks: clean.
- Ruff: **not independently executed in this container because no Ruff executable/module is installed**.

Therefore this ZIP is a **pytest-certified M395.1 candidate** pending the normal local command:

```text
ruff check .
```

If Ruff is clean locally, M395.1 can be promoted to the next certified baseline.
