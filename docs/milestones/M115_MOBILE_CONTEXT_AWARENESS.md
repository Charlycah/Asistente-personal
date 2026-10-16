# M115 — Mobile Context Awareness

## Objective
Provide a governed, declarative snapshot of the current mobile context so later layers can reason about suitability without directly accessing sensors or platform APIs.

## Added contracts
- `MobileActivityState`
- `MobileAttentionState`
- `MobileContextStatus`
- `MobileContextAction`
- `MobileContextPolicy`
- `MobileContextSignal`
- `MobileContextRequest`
- `MobileContextSnapshot`
- `MobileContextRepository`
- `InMemoryMobileContextRepository`
- `MobileContextAwarenessEngine`

## Context dimensions
Activity, attention, network, device lock, charging, battery, orientation, user presence, confidence, and observation freshness.

## Boundary
M115 assembles context metadata only. It performs no sensor acquisition, location lookup, notification delivery, audio, camera, network transport, or operating-system mutation.
