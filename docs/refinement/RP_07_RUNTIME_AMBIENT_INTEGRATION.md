# RP.07 — Runtime Ambient Integration

RP.07 connects the previously isolated RP.06 coordinator to ROBY's official
resident desktop lifecycle.

## Operational flow

A configured local ambient command emits one ephemeral JSON observation. The
resident runtime evaluates it through `AmbientProactiveCoordinator`, consults
the latest RP.05 self-analysis report, and either waits, places a spoken
notification in the desktop queue, or requests one governed camera capture.

## Configuration

- `ROBY_AMBIENT_PROACTIVE_ENABLED=true`
- `ROBY_AMBIENT_INPUT_COMMAND=<local observation command>`
- `ROBY_AMBIENT_AUDIO_CONSENT=true`
- `ROBY_AMBIENT_CAMERA_CONSENT=true` when autonomous visual confirmation is
  desired
- `ROBY_AMBIENT_POLL_SECONDS=2`

The command must print one JSON object with `kind`, `confidence`, `summary`, and
optional privacy, visual-confirmation, and timestamp fields. Raw audio is not
stored by this integration.

## Governance

Private household speech remains suppressed. Camera capture is possible only
when the coordinator requests it, standing camera consent exists, the camera
adapter is enabled, and the existing cooldown and confidence rules pass.
