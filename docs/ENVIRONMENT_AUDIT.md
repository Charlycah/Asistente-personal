# Environment Coverage Audit

- Variables detected through literal Python environment lookups: **55**
- Runtime variables absent from `.env`: **0**
- Runtime variables absent from `.env.example`: **0**

Both environment files now declare every literal variable consumed by the
Python runtime. Existing secret values were preserved and were not copied into
this report.

## RP.10 additions

- `ROBY_CONTINUOUS_COGNITIVE_LOOP_ENABLED`
- `ROBY_COGNITIVE_LOOP_SECONDS`

## Ambient runtime additions

- `ROBY_AMBIENT_PROACTIVE_ENABLED`
- `ROBY_AMBIENT_AUDIO_CONSENT`
- `ROBY_AMBIENT_CAMERA_CONSENT`
- `ROBY_AMBIENT_INPUT_COMMAND`
- `ROBY_AMBIENT_POLL_SECONDS`

The local `.env` explicitly enables the camera capability and records the
standing household audio and camera consent already defined for this private
resident deployment. Ambient observation still requires a valid local command
in `ROBY_AMBIENT_INPUT_COMMAND`; it was intentionally left blank rather than
inventing a device-specific command.
