# M106 — Device Identity and Session Continuity

## Objective
Establish the first cross-device companion contract after Phase X: stable device identity and a governed decision about whether one active companion session is eligible to continue on another device.

## Public contracts
- `DeviceKind`
- `DeviceTrustLevel`
- `DeviceIdentity`
- `CompanionSession`
- `DeviceSessionEndpoint`
- `SessionContinuityStatus`
- `SessionContinuityAction`
- `SessionContinuityPolicy`
- `SessionContinuityRequest`
- `SessionContinuityDecision`
- `SessionContinuityRepository`
- `InMemorySessionContinuityRepository`
- `DeviceSessionContinuityEngine`

## Outcomes
- `ready / resume`: identity, trust, authentication, freshness, availability, and capabilities support a later handoff;
- `review_required / confirm`: the target is recognized rather than trusted or observations are stale/future-dated;
- `blocked / stay`: trust, availability, authentication, or capability constraints prevent continuity;
- `not_applicable / none`: no cross-device transition exists.

## Resume cursor
The cursor is an opaque deterministic digest derived from session identity, revision, conversation reference, source device, and target device. It contains no message content, credential, or personal memory.

## Non-goals
M106 does not execute transport, synchronize state, mutate the active session, transfer secrets, choose channels, or implement Mobile Companion behavior.

## Verification
See `M106_verification.txt` and `tests/test_m106_device_identity_and_session_continuity.py`.
