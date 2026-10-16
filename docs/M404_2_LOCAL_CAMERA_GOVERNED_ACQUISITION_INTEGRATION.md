# ROBY XI.2 — M404.2 Local Camera Governed Acquisition Integration

**Source baseline:** validated M404.1 — 11,131 tests, Ruff clean, M361 synchronized.

## Objective

Connect one existing local-camera capture to the M404 Residential Perception boundary
without changing camera ownership, Vision Core, device control, streaming, persistence or
M403 synchronization.

## Real wiring preserved

The existing productive capture path remains:

`CameraConversationInterceptionPort → CameraAdapter.capture() → CameraProvider.capture()`

M404.2 does not insert `GovernedVisionGateway` or `OfficialVisionCore` into that route and
does not modify `OpenCVCameraClient`.

## Added application bridge

`application/residential_perception/local_camera_acquisition.py` adds:

- `LocalCameraAcquisitionConfig`
- `LocalCameraResidentialObservationAdapter`

One `capture_once()` call:

1. invokes the existing `CameraAdapter.capture()` exactly once;
2. reads only safe frame metadata;
3. creates one `ResidentialPhysicalObservation`;
4. invokes the existing `GovernedResidentialPerceptionAdmission`;
5. returns `(observation, admission)`.

## Identity and provenance

- `resource_id` remains the canonical External Resource Registry identity.
- `camera_index` remains acquisition configuration and never substitutes `resource_id`.
- `frame_id` becomes `acquisition_reference`.
- `captured_at` becomes `observed_at`.
- raw `image_bytes` are excluded from the M404 observation payload.
- the M404 source binding remains the residence/resource/capability contract.

## Failure semantics

Acquisition failure and admission rejection remain distinct:

- camera/provider failure → zero M404 observations;
- successful capture + governance mismatch → observation exists, admission is `REJECTED`.

No stale frame is reused as a current observation.

## Explicitly out of scope

- continuous capture / polling / streaming;
- media persistence or recording;
- IP/RTSP/ONVIF cameras;
- Vision inference;
- device mutation/PTZ;
- M403 synchronization;
- memory/knowledge insertion;
- new camera/source authority.

## Invariants

- exactly one physical capture per M404 acquisition request;
- existing CameraAdapter contract remains unchanged;
- CameraFrame remains neutral;
- OpenCVCameraClient does not import M404;
- successful capture does not imply M404 admission;
- M404 admission does not imply interpretation, persistence, memory or action.

## Validation target

M404.2 adds 11 architecture tests. Expected full-suite total: **11,142 tests**.
