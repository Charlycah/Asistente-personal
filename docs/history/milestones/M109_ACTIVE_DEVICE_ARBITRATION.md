# M109 — Active Device Arbitration

M109 adds a governed arbitration layer for selecting the device that is eligible
to become active for a companion session.

## Public contract

- `DeviceArbitrationCandidate`
- `DeviceArbitrationPolicy`
- `DeviceArbitrationRequest`
- `DeviceArbitrationDecision`
- `DeviceArbitrationStatus`
- `DeviceArbitrationAction`
- `DeviceArbitrationRepository`
- `InMemoryDeviceArbitrationRepository`
- `ActiveDeviceArbitrator`

## Outcomes

- `ready / stay`: keep the current device.
- `ready / switch`: another device is eligible for activation.
- `review_required / confirm`: evidence is stale or ambiguous.
- `blocked / stay`: no candidate is safely eligible.
- `not_applicable / none`: no candidates were supplied.

## Architectural boundary

M109 declares eligibility only. It does not change `active_device_id`, execute a
handoff, transport M108 fragments, activate capabilities, select user interfaces
or communicate with any device.
