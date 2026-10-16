# M110 — Mobile Companion Foundation

M110 establishes the governed operational foundation for ROBY on a mobile device.

It introduces a mobile-specific assessment over M109 arbitration and M107 capability compatibility. The result declares whether a mobile runtime is eligible, which operating mode is effective, and which modalities may later be used.

## Modes
- `foreground`
- `background`
- `hands_free`
- `passive`

## Status and action
- `ready / enable`
- `review_required / confirm`
- `blocked / disable`
- `not_applicable / none`

## Architectural boundary
M110 declares mobile readiness. It does not implement the mobile runtime or perform mobile I/O.
