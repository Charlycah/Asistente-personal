# ROBY XI.2 — M404.1 Residential Perception Foundation

**Source baseline:** official Post-M403 — M361 synchronized, Ruff clean, 11,116 tests passed, 0 regressions.

## Objective

Establish the minimal read-only contractual boundary for residential physical perception
without connecting cameras or sensors productively and without creating a new visual,
resource, transport or cognitive authority.

## Implementation

`core/residential_perception/` adds only:

- `ResidentialPerceptionCapability`;
- `ResidentialPhysicalSourceBinding`;
- `ResidentialPhysicalObservation`;
- `ResidentialPerceptionAdmissionStatus`;
- `ResidentialPerceptionAdmission`;
- `GovernedResidentialPerceptionAdmission`.

## Reused ownership

- M396 `ResidenceId` remains the canonical residence identity.
- `ExternalResourceRegistryAuthority` remains owner of external-resource identity,
  registration and authorization facts.
- `domain.vision.camera_frame.CameraFrame` remains the neutral visual frame contract.
- Vision Core remains the authority for visual interpretation.
- M403 remains the governed distributed synchronization path for later transport.

Residential Perception owns only the physical source/residence binding and admission of
an already-acquired physical observation.

## Read-only acquisition capabilities

The foundation exposes only source-neutral acquisition capabilities:

- `IMAGE_FRAME`;
- `MOTION`;
- `ENVIRONMENT_READING`;
- `CONTACT_STATE`.

These do not represent Vision Core interpretation capabilities.

## Admission

Admission consumes explicit facts and never mutates their owners. An observation is
admitted only when:

- the residence is admitted and not revoked;
- the binding is registered;
- observation/binding residence and resource identities match;
- the External Resource registration matches and is authorized;
- the capability is declared by both binding and resource;
- the timestamp is timezone-aware and not in the future;
- the observation schema is supported;
- the payload contains no credentials, secrets or endpoints.

The result is only `ADMITTED` or `REJECTED`.

## Neutral CameraFrame

No new camera frame type is introduced. The existing
`domain.vision.camera_frame.CameraFrame` contract is reused. Generic Residential
Perception payloads reject raw media bytes; productive media transfer is explicitly
outside this foundation.

## Permanent invariants introduced by M404.1

- physical observation is immutable and read-only;
- source binding is immutable;
- `resource_id` remains the External Resource Registry identity;
- `ResidenceId` remains the M396 identity;
- binding identity is distinct from residence/resource identity;
- acquisition capability is not interpretation capability;
- admission does not imply interpretation, persistence, memory, knowledge or action;
- no parallel resource registry or Vision Core is created;
- no polling, streaming, recording, persistence or device mutation is implemented;
- no credentials/endpoints belong in observation payloads.

## Explicitly out of scope

IP/RTSP/ONVIF integration, continuous streams, sensor polling, frame archives, media
persistence, device control, biometric identification, automatic memory/knowledge
creation and production M403 wiring remain unimplemented.

## Validation target

M404.1 adds 15 architecture tests. Expected full-suite total: **11,131 tests**.
