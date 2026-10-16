# M224.1 — Runtime Identity Compatibility Hotfix

M224.1 restores the M188 identity isolation contract after the official M224 runtime factory exposed a legacy global state-path placeholder through `.env`.

## Behavior

- `.roby/runtime_state.json` is treated as a compatibility placeholder.
- Normal runtime state is derived as:
  `.roby/identity/profiles/<profile>/sessions/<session>/runtime_state.json`
  or below the configured `ROBY_PROFILE_DATA_PATH`.
- A genuinely custom `ROBY_RUNTIME_STATE_PATH` remains authoritative.
- Default identity tests no longer inherit personalized names from a developer's local `.env`.

## Validation

- M188 plus M224.1 focused validation: 23 passed.
- M224.1 new tests: 3 passed.
- Full suite: 5,648 passed.
- Regressions: 0.
