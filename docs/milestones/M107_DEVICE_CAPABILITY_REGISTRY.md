# M107 — Device Capability Registry

## Objective
Provide a governed, queryable registry of device capabilities for later cross-device selection and companion experiences.

## Contracts
- `DeviceCapabilityKind`
- `DeviceCapabilityState`
- `DeviceCapabilityAccess`
- `CapabilityMatchStatus`
- `DeviceCapabilityDescriptor`
- `RegisteredDeviceCapability`
- `DeviceCapabilityRequirement`
- `DeviceCapabilityRegistryPolicy`
- `DeviceCapabilityMatch`
- `DeviceCapabilityRegistryRepository`
- `InMemoryDeviceCapabilityRegistryRepository`
- `DeviceCapabilityRegistry`

## Outcomes
- `satisfied`: every requirement is available and sufficiently trusted;
- `review_required`: freshness, confidence, degraded state, unknown state or consent requires review;
- `unsatisfied`: capability, access, version or feature constraints fail;
- `not_applicable`: no requirements were supplied.

## Non-goals
M107 does not execute device functions, request consent, discover hardware, transfer context, arbitrate the active device, open connections or implement Mobile Companion behavior.
